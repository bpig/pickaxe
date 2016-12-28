from tensorflow.contrib.learn.python.learn.estimators.estimator import *

class JSQestimator(Estimator):
  def _train_model(self,
                   input_fn,
                   steps,
                   feed_fn=None,
                   init_op=None,
                   init_feed_fn=None,
                   init_fn=None,
                   device_fn=None,
                   monitors=None,
                   log_every_steps=100,
                   fail_on_nan_loss=True,
                   max_steps=None):
    # TODO(wicke): Remove this once Model and associated code are gone.
    if hasattr(self._config, 'execution_mode'):
      if self._config.execution_mode not in ('all', 'train'):
        return

      # Stagger startup of worker sessions based on task id.
      sleep_secs = min(
          self._config.training_worker_max_startup_secs,
          self._config.task_id *
          self._config.training_worker_session_startup_stagger_secs)
      if sleep_secs:
        logging.info('Waiting %d secs before starting task %d.', sleep_secs,
                     self._config.task_id)
        time.sleep(sleep_secs)

    # Device allocation
    device_fn = device_fn or self._device_fn

    self._graph = ops.Graph()
    with self._graph.as_default() as g, g.device(device_fn):
      random_seed.set_random_seed(self._config.tf_random_seed)
      global_step = contrib_framework.create_global_step(g)
      features, labels = input_fn()
      self._check_inputs(features, labels)

      # The default return type of _get_train_ops is ModelFnOps. But there are
      # some subclasses of tf.contrib.learn.Estimator which override this
      # method and use the legacy signature, namely _get_train_ops returns a
      # (train_op, loss) tuple. The following else-statement code covers these
      # cases, but will soon be deleted after the subclasses are updated.
      # TODO(b/32664904): Update subclasses and delete the else-statement.
      train_ops = self._get_train_ops(features, labels)
      if isinstance(train_ops, model_fn_lib.ModelFnOps):  # Default signature
        train_op = train_ops.train_op
        loss_op = train_ops.loss
      else:  # Legacy signature
        if len(train_ops) != 2:
          raise ValueError('Expected a tuple of train_op and loss, got {}'.
                           format(train_ops))
        train_op = train_ops[0]
        loss_op = train_ops[1]

      hooks = monitor_lib.replace_monitors_with_hooks(monitors, self)

      ops.add_to_collection(ops.GraphKeys.LOSSES, loss_op)
      return

