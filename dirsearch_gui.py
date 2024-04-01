from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QTextEdit, QLabel, QLineEdit, QFormLayout, QScrollArea
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QSize
import sys
import subprocess
import os
import uuid


class DirsearchGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # 窗口设置
        self.setWindowTitle('Dirsearch GUI - Lxy')
        self.setGeometry(800, 400, 600, 400)  # 调整窗口初始高度
        self.setWindowIcon(QIcon('your-icon-path.png'))  # 设置窗口图标

        # 设置字体
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)

        # 创建中央小部件和布局
        self.centralWidget = QWidget()
        self.centralWidget.setFont(font)
        self.layout = QVBoxLayout()

        # 创建表单布局以添加输入框和标签
        self.formLayout = QFormLayout()
        self.urlTextEdit = QTextEdit()  # 改为多行文本框
        self.paramsLineEdit = QLineEdit()

        # 创建按钮和标签
        self.runButton = QPushButton('运行')
        self.defaultButton = QPushButton('默认参数')
        self.helpToggleButton = QPushButton('显示帮助')
        self.statusLabel = QLabel('状态: 准备就绪')

        # 按钮样式
        buttonStyle = """
            QPushButton {
                color: white;
                background-color: #007BFF;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        self.runButton.setStyleSheet(buttonStyle)
        self.defaultButton.setStyleSheet(buttonStyle)
        self.helpToggleButton.setStyleSheet(buttonStyle)

        # 创建帮助文本框和滚动区域
        self.helpTextEdit = QTextEdit()
        self.helpScrollArea = QScrollArea()
        self.helpScrollArea.setWidget(self.helpTextEdit)
        self.helpScrollArea.setWidgetResizable(True)
        self.helpScrollArea.setMaximumHeight(300)  # 调大最大高度以显示更多帮助文本
        self.helpTextEdit.setStyleSheet("background-color: #F0F0F0;")

        # 设置帮助文本框
        self.set_help_text()
        self.helpTextEdit.setReadOnly(True)

        # 添加表单元素
        self.formLayout.addRow('URLs:', self.urlTextEdit)  # 更改为多行文本框
        self.formLayout.addRow('自定义参数:', self.paramsLineEdit)

        # 为按钮添加事件
        self.runButton.clicked.connect(self.run_dirsearch)
        self.defaultButton.clicked.connect(self.set_default_params)
        self.helpToggleButton.clicked.connect(self.toggle_help_visibility)

        # 为自定义参数输入框添加文本变化事件
        self.paramsLineEdit.textChanged.connect(self.update_status_on_text_change)

        # 组合布局
        self.layout.addLayout(self.formLayout)
        self.layout.addWidget(self.runButton)
        self.layout.addWidget(self.defaultButton)
        self.layout.addWidget(self.helpToggleButton)
        self.layout.addWidget(self.statusLabel)
        self.layout.addWidget(self.helpScrollArea)  # 添加滚动区域到布局中

        # 设置中央小部件和布局
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

    def set_help_text(self):
        help_text = (
            """        其他:
        --version: 显示程序版本号
        -h 或 --help: 显示帮助信息

        基本参数设置:
        -u 或 --url: 指定目标URL，可以使用多次来指定多个目标
        -l 或 --urls-file: 从文件中读取URL列表
        --stdin: 从标准输入读取URL列表
        --cidr: 使用CIDR表示法指定目标
        --raw: 从文件加载原始HTTP请求
        -s 或 --session: 指定会话文件
        --config: 指定配置文件路径

        字典设置:
        -w 或 --wordlists: 指定单词列表文件或目录
        -e 或 --extensions: 指定用逗号分隔的扩展名列表
        -f 或 --force-extensions: 强制为单词列表条目添加扩展名
        -O 或 --overwrite-extensions: 使用指定扩展名覆盖单词列表中的其他扩展名
        --exclude-extensions: 指定要排除的扩展名列表
        --remove-extensions: 从路径中移除所有扩展名
        --prefixes: 为单词列表条目添加前缀
        --suffixes: 为单词列表条目添加后缀
        -U 或 --uppercase: 使用大写字母的单词列表
        -L 或 --lowercase: 使用小写字母的单词列表
        -C 或 --capital: 单词列表中的单词首字母大写

        通用设置:
        -t 或 --threads: 设置线程数
        -r 或 --recursive: 递归扫描
        --deep-recursive: 对每个子目录执行深度递归扫描
        --force-recursive: 对发现的每个路径执行递归扫描
        -R 或 --max-recursion-depth: 设置最大递归深度
        --recursion-status: 设置有效的递归扫描状态码
        --subdirs: 指定要扫描的子目录
        --exclude-subdirs: 指定递归扫描时要排除的子目录
        -i 或 --include-status: 包含特定的HTTP状态码
        -x 或 --exclude-status: 排除特定的HTTP状态码
        --exclude-sizes: 根据响应大小排除
        --exclude-text: 根据响应文本排除
        --exclude-regex: 根据正则表达式排除响应
        --exclude-redirect: 排除匹配特定文本或正则表达式的重定向
        --exclude-response: 排除与特定页面相似的响应
        --skip-on-status: 遇到指定状态码时跳过目标
        --min-response-size: 设置响应的最小长度
        --max-response-size: 设置响应的最大长度
        --max-time: 设置扫描的最大运行时间
        --exit-on-error: 出错时退出扫描

        请求设置:
        -m METHOD, --http-method=METHOD: 设置HTTP方法（默认为GET）
        -d DATA, --data=DATA: 设置HTTP POST请求的数据
        --data-file=PATH: 指定包含HTTP POST请求数据的文件路径
        -H HEADERS, --header=HEADERS: 设置HTTP请求头，可以多次使用以设置多个头
        --headers-file=PATH: 指定包含HTTP请求头的文件路径
        -F, --follow-redirects: 跟随HTTP重定向
        --random-agent: 为每个请求随机选择一个用户代理
        --auth=CREDENTIAL: 设置认证凭证（格式为 用户:密码 或 bearer token）
        --auth-type=TYPE: 设置认证类型（可选：basic, digest, bearer, ntlm, jwt）
        --cert-file=PATH: 指定包含客户端证书的文件路径
        --key-file=PATH: 指定包含客户端证书私钥（未加密）的文件路径
        --user-agent=USER_AGENT: 设置用户代理字符串
        --cookie=COOKIE: 设置HTTP Cookie

        连接设置:
        --timeout=TIMEOUT: 设置连接超时时间
        --delay=DELAY: 设置请求之间的延迟时间
        -p PROXY, --proxy=PROXY: 设置代理URL（HTTP/SOCKS），可多次使用以设置多个代理
        --proxies-file=PATH: 指定包含代理服务器列表的文件路径
        --proxy-auth=CREDENTIAL: 设置代理认证凭证
        --replay-proxy=PROXY: 设置用于重放发现的路径的代理
        --tor: 通过Tor网络代理连接
        --scheme=SCHEME: 设置当原始请求的URL中没有协议时使用的协议（默认为自动检测）
        --max-rate=RATE: 设置每秒最大请求数
        --retries=RETRIES: 设置失败请求的重试次数
        --ip=IP: 指定服务器的IP地址
        --interface=NETWORK_INTERFACE: 指定用于连接的网络接口

        高级设置:
        --crawl: 在响应中寻找并测试新路径

        显示设置:
        --full-url: 在输出中显示完整URL（在静默模式下自动启用）
        --redirects-history: 显示重定向历史
        --no-color: 关闭彩色输出
        -q, --quiet-mode: 开启静默模式，减少输出信息

        输出设置:
        -o PATH/URL, --output=PATH/URL: 设置输出文件，或MySQL/PostgreSQL数据库URL（格式：scheme: //[username:password @]host[:port] /database）
        --format=FORMAT: 设置报告的输出格式（支持：simple, plain, json, xml, md, csv, html, sqlite, mysql, postgresql）
        --log=PATH: 指定日志文件路径"""
            # 可以继续追加帮助文本内容...
        )
        self.helpTextEdit.setText(help_text)

    def toggle_help_visibility(self):
        # 根据当前高度切换滚动区域的高度
        if self.helpScrollArea.maximumHeight() > 0:
            self.helpScrollArea.setMaximumHeight(0)
            self.helpToggleButton.setText('显示帮助')
        else:
            self.helpScrollArea.setMaximumHeight(300)  # 设置最大高度以显示帮助文本
            self.helpToggleButton.setText('隐藏帮助')

    def run_dirsearch(self):
        os.makedirs('urls', exist_ok=True)  # 创建文件夹
        file_name = uuid.uuid4().hex + '.txt'  # 生成随机文件名
        file_path = os.path.join('urls', file_name)  # 路径拼接

        # 将URLs写入文件
        with open(file_path, 'w') as file:
            urls = self.urlTextEdit.toPlainText().strip()
            file.write(urls)

        params = self.paramsLineEdit.text()
        command = f'cmd.exe /c start cmd.exe /k python dirsearch.py -l {file_path} {params}'
        subprocess.Popen(command, shell=True)
        self.statusLabel.setText('状态: 正在扫描...')

    def set_default_params(self):
        self.paramsLineEdit.setText('-i 200-399 -t 300 --random-agent')
        self.statusLabel.setText('状态: 已设置默认参数')

    def update_status_on_text_change(self):
        if not self.paramsLineEdit.text():
            self.statusLabel.setText('状态: 准备就绪')


app = QApplication(sys.argv)
window = DirsearchGUI()
window.show()
sys.exit(app.exec())
