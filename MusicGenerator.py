import pyxel

class MusicGenerator:
    def __init__(self):
        self.base_melody = [0, 2, 4, 5, 7, 9, 11, 12]  # Cメジャースケール
        self.transposed_melody = []
        self.sound_index = 0
        self.transpose(5)  # 例として5半音分トランスポーズ
        self.create_music()

    def transpose(self, n):
        """メロディをn半音分トランスポーズする関数"""
        self.transposed_melody = [(note + n) % 12 for note in self.base_melody]

    def create_music(self):
        """メロディとパーカッションをpyxelのmusicAPIで定義する関数"""
        for i, note in enumerate(self.transposed_melody):
            note_name = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"][note] + "3"
            pyxel.sound(i).set(note_name, "s", "4", "n", 25)
            
        # 強調されたパーカッション音を設定
        pyxel.sound(8).set("c1", "p", "7", "s", 15)

        # メロディラインとパーカッションラインを音楽として定義
        melody_channel = [i for i in range(len(self.transposed_melody))]
        percussion_channel = [8] * len(self.transposed_melody)  # パーカッション音を再生するチャンネル

        pyxel.music(0).set(melody_channel, percussion_channel, [], [])

    def play_music(self):
        pyxel.playm(0)
