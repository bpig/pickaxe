import json
import random
import sys
import numpy as np
import time
import math

class TimeLog:
    def __enter__(self):
        self.t = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "%.2fs" % (time.time() - self.t)

class QuadraticCost(object):
    @staticmethod
    def fn(a, y):
        return 0.5 * np.linalg.norm(a - y) ** 2

    @staticmethod
    def delta(z, a, y):
        return (a - y) * sigmoid_prime(z)

class CrossEntropyCost(object):
    @staticmethod
    def fn(a, y):
        return np.sum(np.nan_to_num(-y * np.log(a) - (1 - y) * np.log(1 - a)))

    @staticmethod
    def delta(z, a, y):
        return a - y

#### Main Network class
class Network(object):
    def __init__(self, sizes, cost=CrossEntropyCost):
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.default_weight_initializer()
        self.cost = cost

    def default_weight_initializer(self):
        self.biases = [np.random.randn(y, 1) for y in self.sizes[1:]]
        self.weights = [np.random.randn(y, x) / np.sqrt(x)
                        for x, y in zip(self.sizes[:-1], self.sizes[1:])]

    def large_weight_initializer(self):
        self.biases = [np.random.randn(y, 1) for y in self.sizes[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(self.sizes[:-1], self.sizes[1:])]

    def feedforward(self, a):
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a) + b)
        return a

    def getArgs(self):
        data = open("args").readlines()[:2]
        lmbda = float(data[0][7:])
        eta = float(data[1][6:])
        return lmbda, eta

    def SGD(self, training_data, epochs, mini_batch_size, eta,
            lmbda=0.0,
            evaluation_data=None,
            monitor_evaluation_cost=False,
            monitor_evaluation_accuracy=False,
            monitor_training_cost=False,
            monitor_training_accuracy=False):
        if evaluation_data:
            n_data = len(evaluation_data)
        n = len(training_data)
        evaluation_cost, evaluation_accuracy = [], []
        training_cost, training_accuracy = [], []
        for j in xrange(epochs):
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k + mini_batch_size]
                for k in xrange(0, n, mini_batch_size)]

            with TimeLog():
                # lmbda, eta = self.getArgs()
                print "lmbda %.2f, eta %.2f" % (lmbda, eta)
                for mini_batch in mini_batches:
                    self.update_mini_batch(
                        mini_batch, eta, lmbda, len(training_data))
                    
            fn = sys.argv[3] + "/model_" + str(j)
            self.save(fn)
            print "Epoch %s training complete" % j
            if monitor_training_cost:
                cost = self.total_cost(training_data, lmbda)
                training_cost.append(cost)
                print "Cost on training macro: {}".format(cost)
            if monitor_training_accuracy:
                accuracy = self.accuracy(training_data, convert=True)
                training_accuracy.append(accuracy)
                print "Accuracy on training macro: {} ".format(
                    accuracy)
            if monitor_evaluation_cost:
                cost = self.total_cost(evaluation_data, lmbda, convert=True)
                evaluation_cost.append(cost)
                print "Cost on evaluation macro: {}".format(cost)
            if monitor_evaluation_accuracy:
                accuracy = self.accuracy(evaluation_data, convert=True)
                evaluation_accuracy.append(accuracy)
                print "Accuracy on evaluation macro: {}".format(
                    accuracy)
            print
        return evaluation_cost, evaluation_accuracy, \
               training_cost, training_accuracy

    def update_mini_batch(self, mini_batch, eta, lmbda, n):
        """Update the network's weights and biases by applying gradient
        descent using backpropagation to a single mini batch.  The
        ``mini_batch`` is a list of tuples ``(x, y)``, ``eta`` is the
        learning rate, ``lmbda`` is the regularization parameter, and
        ``n`` is the total size of the training macro set.

        """
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb + dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw + dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [(1 - eta * (lmbda / n)) * w - (eta / len(mini_batch)) * nw
                        for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b - (eta / len(mini_batch)) * nb
                       for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x]  # list to store all the activations, layer by layer
        zs = []  # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation) + b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
        # backward pass
        delta = self.cost.delta(zs[-1], activations[-1], y)
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        # Note that the variable l in the loop below is used a little
        # differently to the notation in Chapter 2 of the book.  Here,
        # l = 1 means the last layer of neurons, l = 2 is the
        # second-last layer, and so on.  It's a renumbering of the
        # scheme in the book, used here to take advantage of the fact
        # that Python can use negative indices in lists.
        for l in xrange(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l + 1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l - 1].transpose())
        return nabla_b, nabla_w

    def accuracy(self, data, convert=False):
        if convert:
            results = [(np.argmax(self.feedforward(x)), np.argmax(y))
                       for (x, y) in data]
        else:
            results = [(np.argmax(self.feedforward(x)), y)
                       for (x, y) in data]
        ct = [0] * 4
        yt = [0] * 4
        at = [0] * 4
        for x, y in results:
            at[x] += 1
            yt[y] += 1
            if x == y:
                ct[y] += 1
        tt = str(sum(ct)) + "/" + str(sum(yt)) + ", " + str(1.0 * sum(ct) / sum(yt))
        ans = "%s\n%d / %d, %d / %d, %d / %d, %d / %d, %f\n                                                  %s" % \
            (str(at), ct[0], yt[0], ct[1], yt[1], ct[2], yt[2], ct[3], yt[3], \
                 ct[3] / (at[3]+1.0), tt)
        return ans
        #return sum(int(x == y) for (x, y) in results)

    def total_cost(self, data, lmbda, convert=False):
        cost = 0.0
        for x, y in data:
            a = self.feedforward(x)
            if convert:
                y = vectorized_result(y)
            cost += self.cost.fn(a, y) / len(data)
        cost += 0.5 * (lmbda / len(data)) * sum(
            np.linalg.norm(w) ** 2 for w in self.weights)
        return cost

    def save(self, filename):
        data = {"sizes": self.sizes,
                "weights": [w.tolist() for w in self.weights],
                "biases": [b.tolist() for b in self.biases],
                "cost": str(self.cost.__name__)}
        f = open(filename, "w")
        json.dump(data, f)
        f.close()

#### Loading a Network
def load(filename):
    f = open(filename, "r")
    data = json.load(f)
    f.close()
    cost = getattr(sys.modules[__name__], data["cost"])
    net = Network(data["sizes"], cost=cost)
    net.weights = [np.array(w) for w in data["weights"]]
    net.biases = [np.array(b) for b in data["biases"]]
    return net

def sigmoid(z):
    """The sigmoid function."""
    f = 1.0 / (1.0 + np.exp(-z))
    # f = np.nan_to_num(f)
    return f
    # epsilon = -1e2
    # z0 = z
    # z0 = np.minimum(-epsilon, z0)
    # z0 = np.maximum(epsilon, z0)
    # try:
    #     f = 1.0 / (1.0 + np.exp(-z0))
    # except:
    #     print z0, z
    # # f = np.nan_to_num(f)
    # return f

def sigmoid_prime(z):
    return sigmoid(z) * (1 - sigmoid(z))

ydim = 0
def vectorized_result(j):
    # 0.737 ~ 1.34
    global ydim
    idx = 0

    # ydim = 2
    # e = np.zeros((ydim, 1))
    # if j <= 1.0:
    #     idx = 0
    # else:
    #     idx = 1

    ydim = 4
    e = np.zeros((ydim, 1))
    if j <= 0.95:
        idx = 0
    elif j <= 1.00:
        idx = 1
    elif j <= 1.05:
        idx = 2
    else:
        idx = 3
    e[idx] = 1.0
    return e

def loadStock(filename):
    ans = []
    c = 0
    total = int(sys.argv[2])
    dim = 0
    ct = [0] * 4
    e = 0
    for l in open(filename):
        l = l.strip()
        if not l:
            continue
        pos = l.find(":")
        l = l[pos+1:]
        items = l.split(",")
        win = math.ceil(float(items[-2]) * 60)
        day = 60 * (7.0 / 5) + 4
        if win > day:
            e += 1
            continue
        dim = len(items) - 2
        xx = map(float, items[:-2])
        x = np.reshape(xx, (dim, 1))
        yy = float(items[-1])
        y = vectorized_result(yy)
        ct[np.argmax(y)] += 1
        ans += [(x, y)]
        c += 1
        if c == total:
            break

    total = min(len(ans), total)
    print ct, total, total + e

    ans = ans[:total]
    return ans[:int(total * .8)], ans[int(total * .8):int(total * .8) + 4000], \
           ans[int(total * .8) + 4000:int(total * .8) + 8000], dim

if __name__ == '__main__':
    with TimeLog():
        training_data, validation_data, test_data, dim = loadStock(sys.argv[1])
    print dim
    np.seterr(over='raise')

    net = Network([dim, 100, 30, ydim], cost=CrossEntropyCost)
    # net = load("model/model_35")
    minibatch = 16
    eta = 0.01
    lmbda = 0.01
    net.SGD(training_data, 1000, minibatch, eta,
            lmbda=lmbda, evaluation_data=validation_data[:5000],
            monitor_evaluation_accuracy=True,
            monitor_evaluation_cost=False,
            monitor_training_accuracy=True,
            monitor_training_cost=False)
