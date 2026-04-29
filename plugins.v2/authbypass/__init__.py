# -*- coding: utf-8 -*-
"""
用户认证强制通过插件
用于开发调试环境，强制设置 auth_level >= 2 跳过站点认证检查
"""

from typing import Tuple, Optional, List, Dict, Any
from app.plugins import _PluginBase


class AuthBypass(_PluginBase):
    """用户认证强制通过插件"""

    plugin_name = "用户认证强制通过"
    plugin_desc = "强制设置用户认证级别为2，跳过站点认证检查，用于开发调试环境"
    plugin_order = 9999

    def __init__(self):
        super().__init__()
        self._enabled = False
        self._original_siteshelper_clz = None

    def get_state(self) -> bool:
        return self._enabled

    def init_plugin(self, config: dict = None):
        """初始化插件生效配置"""
        self._enabled = config.get("enabled", False) if config else False
        self._apply_bypass(self._enabled)

    def _apply_bypass(self, enabled: bool):
        """应用/移除认证绕过"""
        try:
            from app.helper import sites as sites_module
            if enabled:
                self._original_siteshelper_clz = sites_module.SitesHelper
                original_clz = self._original_siteshelper_clz

                class BypassSitesHelper:
                    """强制返回 auth_level=2 的 SitesHelper 包装类"""

                    _original_clz = original_clz

                    def __init__(self):
                        self._wrapped = self._original_clz()

                    @property
                    def auth_level(self):
                        return 2

                    def __getattr__(self, name):
                        return getattr(self._wrapped, name)

                sites_module.SitesHelper = BypassSitesHelper
            else:
                if self._original_siteshelper_clz:
                    from app.helper import sites as sites_module
                    sites_module.SitesHelper = self._original_siteshelper_clz
        except ImportError as e:
            print(f"SitesHelper 模块未找到: {e}")

    def stop_service(self):
        """停止插件服务时移除 patch"""
        self._apply_bypass(False)

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        form = [
            {
                "component": "VSwitch",
                "props": {
                    "model": "enabled",
                    "label": "启用强制认证通过",
                    "color": "primary",
                    "hint": "开启后跳过站点用户认证检查",
                    "persistent-hint": True
                }
            },
            {
                "component": "VAlert",
                "props": {
                    "type": "warning",
                    "model": True,
                    "title": "警告",
                    "text": "此功能仅用于开发调试环境，请在生产环境关闭！",
                    "show": "{{enabled}}",
                    "class": "mt-4"
                }
            }
        ]
        return form, {"enabled": False}

    def get_page(self) -> Optional[List[dict]]:
        return None

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    def get_command(self) -> List[Dict[str, Any]]:
        return []

    @staticmethod
    def get_render_mode():
        return "vuetify", None