import pyxel

class Camera:
    ZOOM_LEVEL_ENEMY = 1.2
    ZOOM_LEVEL_HEALTH = 0.8
    LERP_ALPHA = 0.1
    LERP_SWITCH = False

    def __init__(self, x, y, fov_x, fov_y, zoom_level=1.0):
        ### fov_x, fov_y: Field of View。カメラの視野角を表す。
        self.x = x
        self.y = y
        self.fov_x = fov_x
        self.fov_y = fov_y
        self.zoom_level = zoom_level
        self.fade_value = 0
        #for panning
        self.panning = False
        self.pan_target_x = 0
        self.pan_origin = None
        self.current_frame = 0
        self.pan_duration = 0
        self.wait_duration = 0
        self.return_duration = 0

    def is_object_in_view(self, obj):
        half_fov_x = self.fov_x / 2
        half_fov_y = self.fov_y / 2
        return self.x - half_fov_x <= obj.x <= self.x + half_fov_x and \
               self.y - half_fov_y <= obj.y <= self.y + half_fov_y

    def lerp(self, start, end, alpha):
        return start + alpha * (end - start)

    def clamp_position(self, pos, max_val):
        ###機能概要：カメラの位置を制限する。
        ###引数：pos: カメラの位置。max_val: カメラの最大位置。
        # return max(0, min(pos, max_val - pyxel.width))
        # return max(0, min(pos, max_val - self.fov_x))
        # return max(0, min(pos, max_val))
        return max(0, min(pos, max_val - self.fov_x))

    def start_pan(self, target_x, pan_frames, wait_frames, return_frames):
        self.panning = True
        self.pan_target_x = target_x
        self.pan_origin = (self.x, self.y)
        self.current_frame = 0
        self.pan_duration = pan_frames
        self.wait_duration = wait_frames
        self.return_duration = return_frames

    def update(self, target_x, target_y, map_width=None, map_height=None):
        ###panning
        if self.panning:
            self.handle_pan()
        else:
            # print(f"target_x: {target_x}, target_y: {target_y}, map_width: {map_width}, map_height: {map_height}")
            half_screen_x = pyxel.width // 2
            half_screen_y = pyxel.height // 2

            target_x = self.clamp_position(target_x - half_screen_x, map_width)
            target_y = self.clamp_position(target_y - half_screen_y, map_height)

            ###Lerp使用するとき
            # self.x = self.lerp(self.x, target_x, self.LERP_ALPHA)
            # self.y = self.lerp(self.y, target_y, self.LERP_ALPHA)

            ###Lerp使用しないとき
            self.x = target_x
            self.y = target_y

    def apply(self, obj):
        ###draw_x, draw_yは、カメラの位置を考慮したオブジェクトの描画位置
        # ズームレベルも考慮
        obj.draw_x = (obj.x - self.x) * self.zoom_level
        obj.draw_y = (obj.y - self.y) * self.zoom_level

    def apply_layer(self, obj, layer_speed):
        # レイヤーごとにスクロール速度を適用
        obj.draw_x = (obj.x - self.x) * layer_speed
        obj.draw_y = (obj.y - self.y) * layer_speed

    def dynamic_view(self, condition):
        # ゲームの状況に応じてズームレベルを動的に変更
        if condition == 'many_enemies':
            self.zoom_level = 1.2
        elif condition == 'low_health':
            self.zoom_level = 0.8

    def auto_scroll(self, speed):
        # カメラを自動でスクロール
        self.x += speed

    def fade(self, type, speed):
        # フェードイン・アウトの処理
        # typeに'in'または'out'を指定
        if type == 'in':
            self.fade_value = max(0, self.fade_value - speed)
        elif type == 'out':
            self.fade_value = min(255, self.fade_value + speed)
        pyxel.rect(0, 0, pyxel.width, pyxel.height, self.fade_value)

    def handle_pan(self):
        total_frames = self.pan_duration + self.wait_duration + self.return_duration
        if self.current_frame >= total_frames:
            self.panning = False
            return
        elif self.current_frame < self.pan_duration:
            t = self.current_frame / self.pan_duration
            self.x = self.lerp(self.pan_origin[0], self.pan_target_x, t)
            # self.y = self.lerp(self.pan_origin[1], self.pan_target.y, t)
        elif self.current_frame < self.pan_duration + self.wait_duration:
            pass  # just wait
        else:
            t = (self.current_frame - self.pan_duration - self.wait_duration) / self.return_duration
            self.x = self.lerp(self.pan_target_x, self.pan_origin[0], t)
            # self.y = self.lerp(self.pan_target.y, self.pan_origin[1], t)
        self.current_frame += 1