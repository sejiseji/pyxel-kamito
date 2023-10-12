####--------------------------------------------------------------------
# ゲームオブジェクト
class GameObject:
	def __init__(self, x=0, y=0):
        # パラメタ初期化
		self.exists = False
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.width = 0
		self.height = 0
		self.checkable = False
		self.message = ""
		self.message_created = False
		
        ###会話とシナリオに付随したテキスト返却のための管理パラメタ
        ###シーン番号、シナリオ番号、返却テキスト番号（進行に合わせて返却のたびにカウントアップ、ただし質問中はそのまま）、質問中フラグ、返答結果番号
		self.scene_no = 0 ### シーン番号
		self.scenario_no = 0 ### シナリオ番号
		self.rtn_txt_no = 0 ### 返却テキスト番号
		self.flg_waiting_responce = False ### 相手からの返答待ち（＝質問中）フラグ
		self.conversation_with = 0
		self.responce_no = 0 ### 返答結果番号
