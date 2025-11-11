from qfluentwidgets import FluentIcon
import time
import cv2
import re

from ok import Logger, TaskDisabledException
from src.tasks.BaseCombatTask import BaseCombatTask
from src.tasks.DNAOneTimeTask import DNAOneTimeTask
from src.tasks.CommissionsTask import CommissionsTask

logger = Logger.get_logger(__name__)


class AutoSkill(DNAOneTimeTask, CommissionsTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = FluentIcon.FLAG
        self.setup_commission_config()
        # 移除该任务不需要的配置项
        keys_to_remove = ["委托手册", "启用自动穿引共鸣", "自动选择首个密函和密函奖励"]
        for key in keys_to_remove:
            self.default_config.pop(key, None)

        self.default_config.update({
            '主画面侦测': True,
            '任务超时时间': 120,
        })
        self.config_description = {
            '主画面侦测': '如果不在可操控角色的画面则结束任务',
            '任务超时时间': '放弃任务前等待的秒数',
        }
        
        self.name = "自动释放技能"
        self.action_timeout = 10
        
    def run(self):
        DNAOneTimeTask.run(self)
        try:
            return self.do_run()
        except TaskDisabledException as e:
            pass
        except Exception as e:
            logger.error('AutoCombatSkill error', e)
            raise

    def do_run(self):
        self.load_char()
        _skill_time = 0
        self.wait_until(self.in_team, time_out=30)
        while True:
            if self.in_team():
                _skill_time = self.use_skill(_skill_time)
            else:
                if self.config.get('主画面侦测', False):
                    self.log_info_notify('任务完成')
                    self.soundBeep()
                    return
            if time.time() - self.start_time >= self.config.get('任务超时时间', 120):
                self.log_info_notify('任务超时')
                self.soundBeep()
                return
            self.sleep(0.2)
