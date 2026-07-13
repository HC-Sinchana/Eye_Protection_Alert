from unittest.mock import patch

from eyeguard.notifier import Notifier


def test_notify_respects_cooldown():
    notifier = Notifier(title="t", message="m", cooldown_s=100.0, play_sound=False)
    with patch.object(notifier, "_notify_console") as mock_console:
        notifier.notify()
        notifier.notify()  # should be suppressed by cooldown
        assert mock_console.call_count == 1


def test_notify_falls_back_through_backends():
    notifier = Notifier(title="t", message="m", cooldown_s=0.0, play_sound=False)
    with (
        patch.object(notifier, "_notify_plyer", side_effect=Exception("no plyer")),
        patch.object(notifier, "_notify_tkinter", side_effect=Exception("no display")),
        patch.object(notifier, "_notify_console") as mock_console,
    ):
        notifier.notify()
        mock_console.assert_called_once()
