import signal


class SignalHandler:
    def __init__(self) -> None:
        self._received_signal = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame) -> None:
        self._received_signal = True

    def received_signal(self) -> bool:
        return self._received_signal
