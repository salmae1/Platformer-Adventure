import time
import arcade
from collectable import Coin, Apple
from gameview import GameView
from unittest.mock import MagicMock
from _pytest.monkeypatch import MonkeyPatch



def test_effect_on_view(window: arcade.Window) -> None:
    view = GameView()
    window.show_view(view)

    coin = Coin(100, 200)
    coin.effect_on_view(view)
    assert view.score == 1, "Le score doit augmenter après collecte de la pièce"

    before = time.time()
    apple = Apple(150, 250)
    apple.effect_on_view(view)

    after = time.time()
    expected_min = before + 3
    expected_max = after + 3
    assert expected_min <= view.player.hidden_time <= expected_max, "hidden_time doit être ≈ now + 3s"

    delta = view.player.hidden_time - time.time()
    assert 2.9 <= delta <= 3.1

def test_collect(window: arcade.Window, monkeypatch: MonkeyPatch) -> None:
    mock_sound = MagicMock()
    mock_play_sound = MagicMock()
    monkeypatch.setattr(arcade, "load_sound", lambda *args, **kwargs: mock_sound)   
    monkeypatch.setattr(arcade, "play_sound", mock_play_sound)

    view = GameView()
    window.show_view(view)

    coin = Coin(100, 100)
    coin.collect(view)

    assert view.score == 1, "Le score doit augmenter"
    mock_play_sound.assert_called_with(mock_sound, loop=False)

    apple = Apple(150, 150)
    apple.collect(view)

    assert view.player.hidden_time > time.time(), "hidden_time doit être mis à jour"