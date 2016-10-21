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
          self._config.task *
          self._config.training_worker_session_startup_stagger_secs)
      if sleep_secs:
        logging.info('Waiting %d secs before starting task %d.', sleep_secs,
                     self._config.task)
        time.sleep(sleep_secs)

    # Device allocation
    device_fn = device_fn or self._device_fn

    self._graph = ops.Graph()
    with self._graph.as_default() as g, g.device(device_fn):
      random_seed.set_random_seed(self._config.tf_random_seed)
      global_step = contrib_framework.create_global_step(g)
      features, targets = input_fn()
      self._check_inputs(features, targets)
      train_op, loss_op = self._get_train_ops(features, targets)

      # Add default monitors.
      if monitors is None:
        monitors = []

      hooks = [m for m in monitors
               if isinstance(m, session_run_hook.SessionRunHook)]

      deprecated_monitors = [
          m for m in monitors
          if not isinstance(m, session_run_hook.SessionRunHook)
      ]

      supervisor_is_chief = self._config.is_chief
      if not supervisor_is_chief:
        # Prune list of monitor to the ones runnable on all workers.
        deprecated_monitors = [m for m in deprecated_monitors
                               if m.run_on_all_workers]

      # Setup monitors.
      for monitor in deprecated_monitors:
        monitor.set_estimator(self)

      if deprecated_monitors:
        hooks.append(monitor_lib.RunHookAdapterForMonitors(deprecated_monitors))
      return
