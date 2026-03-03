"""
HTTP 工具函数模块
"""
import ssl
import urllib.request
import json
from typing import Optional, Tuple, Dict


def create_ssl_context() -> ssl.SSLContext:
    """创建禁用证书验证的 SSL 上下文"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Tuple[str, Dict]:
    """
    HTTP GET 请求
    
    Args:
        url: 请求URL
        headers: 请求头
        timeout: 超时时间
        
    Returns:
        tuple: (响应体字符串, 响应头字典)
        失败返回 (-1, {})
    """
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout, context=create_ssl_context()) as response:
            resp_text = response.read().decode("utf-8")
            resp_headers = dict(response.getheaders())
            return resp_text, resp_headers
    except Exception as e:
        print(f"[HTTP] GET 请求失败: {url}, 错误: {e}")
        return -1, {}


def http_post(url: str, body: str, headers: Dict[str, str], timeout: int = 30) -> Tuple[str, Dict]:
    """
    HTTP POST 请求
    
    Args:
        url: 请求URL
        body: 请求体
        headers: 请求头
        timeout: 超时时间
        
    Returns:
        tuple: (响应体字符串, 响应头字典)
        失败返回 (-1, {})
    """
    try:
        data = body.encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout, context=create_ssl_context()) as resp:
            resp_text = resp.read().decode("utf-8")
            resp_headers = dict(resp.headers)
            return resp_text, resp_headers
    except Exception as e:
        print(f"[HTTP] POST 请求失败: {url}, 错误: {e}")
        raise
