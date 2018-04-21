# qzone_spider

一个爬取QQ空间信息的爬虫的模块。使用Python 3.6。

本描述文件比较技术向，如果你只是想使用现成的爬虫，只看前两节就行了。但是如果你想借此开发爬虫，你务必看完。

## 使用方法

qzone_spider附带一些数据库的操作工具，目前支持MySQL（`db_control_mysql`）、PostgreSQL（`db_control_postgresql`）、SQLite（`db_control_sqlite`）。它们未集成在qzone_spider包内，需要通过`from qzone_spider import db_control_%s`这样的方式导入。

### 要求与准备

系统方面，只要能够运行Python 3的最新版本就可以。建议有图形界面用于偶尔需要验证时进行操作，但大多数情况下都不需要图形界面。

你需要安装Python 3的最新版本，并安装以下第三方模块：selenium、requests。

你需要安装Chrome或Chromium，并安装好chromedriver。

你需要准备好将要连接的数据库。如果是SQLite，则不需要这么做。

如果你使用MySQL作为数据库，你还需要安装pymysql模块；如果你使用PostgreSQL作为数据库，你还需要安装psycopg2模块。

当然，如果你有能力，也可以自行使用别的配置，只不过后面需要自己写代码。

### 配置

我们接下来以MySQL数据库为例介绍使用方法。

更改qzone_spider中的svar.py：

```python
dbType = 'MySQL'			# 数据库类型，目前只是为了标识用
dbURL = 'localhost'			# 数据库地址，如果是SQLite则写数据库文件路径名
dbPort = 3306				# 数据库端口号，如果是SQLite则忽略
dbUsername = 'root'			# 数据库用户名，如果是SQLite则忽略
dbPassword = 'root'			# 数据库密码，如果是SQLite则忽略
dbDatabase = 'mood2'		# 数据库名称，如果是SQLite则忽略

emotionParse = True			# 是否转换表情符号

loginFailTime = 2			# 登录的时候错误重试次数
getRoughDataFailTime = 2	# 获取粗JSON时错误重试次数
getFineDataFailTime = 2		# 获取细JSON时错误重试次数

loginWaitTime = 3			# 登录的时候等待时间（秒）
scanWaitTime = 20			# 扫码的时候等待时间
spiderWaitTime = 5			# 爬虫每次执行后的等待时间
errorWaitTime = 600			# 发生错误后重试的等待时间
```

在爬虫文件的目录下打开Python，执行：

```python
import qzone_spider
from qzone_spider import db_control_mysql as db_control
db_control.db_init()
```

在爬虫的执行文件的头部需要写入：

```python
import qzone_spider
from qzone_spider import db_control_mysql as db_control
```

如果你在Unix系统或类Unix系统中使用root账户，登录时使用调试模式会报错。这时请在get_login_info.py中找到下面的语句，并在logger语句下加一行代码：`chrome_options.add_argument('--no-sandbox')`，见下：

```python
        if debug:
            logger.info('''You are in debug mode. It requires GUI environment. 
If you are in console without GUI environment or SSH, please exit. 
If you really need it, please run it in GUI environment. 
Or you need to delete the attribute 'debug=True' in %s''' % __name__)
            chrome_options.add_argument('--no-sandbox')
```



接下来的请参照后面的介绍自行编写。我也写了一个示例爬虫（spider_example.py），供参考。

## 示例爬虫

示例爬虫的主要功能是：使用某个QQ号取爬取某个QQ号的若干条动态，并存至之前设置的数据库。

程序设置的是SQLite数据库。如果你需要使用别的数据库，请更改以下地方的代码：

```python
from qzone_spider import db_control_sqlite as db_control

db_control.db_write_fine(parse_fine)
```

### 运行方式

请在命令行（Windows下的命令提示符、PowerShell，Unix或类Unix系统下的控制台、终端或SSH）下进行操作。

Windows下：

```cmd
> python ./spider_example.py -u 作为爬虫的QQ号 -t 爬取的QQ号 -q 爬取动态数量
```

Unix或类Unix系统下：
```shell
$ python3 ./spider_example.py -u 作为爬虫的QQ号 -t 爬取的QQ号 -q 爬取动态数量
```

如果是在Unix或类Unix系统下，可以在赋予spider_example.py的执行权限后，省略掉`python3`执行：

```shell
$ ./spider_example.py -u 作为爬虫的QQ号 -t 爬取的QQ号 -q 爬取动态数量
```

其中，爬取动态数量应为20的倍数。

### 验证

运行开始的时候需要输入作为爬虫的QQ号的密码（注意，输入密码的时候没有任何提示），输完后按回车，爬虫即可运行。

一般来说，第一次使用，QQ空间会提示验证。这时，请修改代码，将

```python
cookies, gtk, qzonetoken = qzone_spider.account_login(QQ, password)
```

更改为

```python
cookies, gtk, qzonetoken = qzone_spider.account_login(QQ, password, debug=True)
```

再次运行。这次需要有图形界面。浏览器将会显示以进行验证。

一般来说，在一台设备登录QQ后，很长时间都不需要验证。所以，验证完后可以把代码改回来。

## 函数

如无说明，以下函数在使用前可以通过导入模块的方式导入。如：

```python
import qzone_spider
a, b, c = qzone_spider.account_login('123456', 'password', debug=True)
```

但涉及到数据库操作的模块需要另外导入。如：

```python
from qzone_spider import db_control_mysql as db_control
db_control.db_init()
```

### `account_login`

通过QQ号和密码，模拟登录手机网页版的QQ空间，以获取登录信息。

```python
account_login(qq, password, debug=False)
```

参数：

1. `qq`：字符串类型，QQ号。
2. `password`：字符串类型，QQ密码
3. `debug`：布尔类型，是否开启调试模式。默认值为False。当它设置为False时，开启浏览器的无头模式，启动时没有界面；当遇到需要验证的情况时，程序会提示需要打开调试模式，并退出。否则，浏览器不会开启无头模式，可以显示界面，以便验证和调试，但程序也会提示调试模式。

函数会返回三个值：

1. 字典类型，Cookies。
2. 字符串类型，gtk。
3. 字符串类型，qzonetoken。

如果中途发生错误，输出的值均为`None`。

### `scan_login`

通过扫码的方式登录PC端的QQ空间，以获取登录信息。

```python
scan_login()
```

无参数。

运行时需要使用GUI界面，并且监视浏览器的行为，当出现二维码的时候使用手机QQ扫码即可。

函数的输出与`account_login`相同。

### `get_rough_json`

获取QQ空间动态的粗JSON。一般来说，一次可以爬取多条动态的粗JSON数据。

```python
get_rough_json(qq, start, msgnum, replynum, cookies, gtk, qzonetoken)
```

参数：

1. `qq`：字符串类型，QQ号。
2. `start`：整数类型，开始的位置。
3. `msgnum`：整数类型，一次获取获取的动态条数。范围为1至20。
4. `replynum`：整数类型，每条动态获取的回复数。范围为0至10。
5. `cookies`：字典类型，获取登录信息时得到的Cookies。
6. `gtk`：字符串类型，获取登录信息时得到的gtk。
7. `qzonetoken`：字符串类型，获取登录信息时得到的qzonetoken。

函数会返回三个值：

1. 整数类型，爬取数据时的时间戳。
2. 整数类型，爬取得到的最后一条动态的编号。
3. 列表类型，爬取的动态的粗JSON数据的Python表达方式。

如果中途发生错误，分以下情况：

1. 开始位置超过动态编号末尾（一般来说，如果你一直爬取某个账号的动态，会这样，表示爬取完成），或者是返回结果异常（可能是因为登录信息失效）：返回三个整数值：`0, -1, 0`。
2. 爬取失败：返回三个整数值：`0, -1, -1`。

### `get_fine_json`

获取QQ空间动态的细JSON。一次只能爬取一条动态的细JSON数据。

```python
get_fine_json(qq, tid, cookies, gtk, qzonetoken)
```

参数：

1. `qq`：字符串类型，QQ号。
2. `tid`：字符串类型，动态的编号。
3. `cookies`：字典类型，获取登录信息时得到的Cookies。
4. `gtk`：字符串类型，获取登录信息时得到的gtk。
5. `qzonetoken`：字符串类型，获取登录信息时得到的qzonetoken。

函数会返回两个值：

1. 整数类型，爬取数据时的时间戳。
2. 字典类型，爬取的动态的细JSON数据的Python表达方式。

如果爬取失败，返回两个整数值：`0, -1`。

根据经验，不要频繁使用该函数，否则会无法正常使用QQ空间的功能，具体特征是：当打开动态的详细页时，会提示“操作失败”。这种状态少则持续一个小时，多则一天，不知道会不会永久受影响。

### `rough_json_parse`

对QQ空间动态的粗JSON数据进行，取有用的数据重新组合。

```python
rough_json_parse(rough_json_list, ordernum, catch_time=0)
```

参数：

1. `rough_json_list`：列表类型，爬取的动态的粗JSON数据的Python表达方式。
2. `ordernum`：整数类型，`rough_json_list`中的列表编号，代表其中的某一条动态的编号。
3. `catch_time`：整数类型，爬取数据时的时间戳。默认值为0。

函数会返回一个字典类型的数据，表示解析后的动态的粗数据的JSON的Python表达方式。

### `emotion_parse`

根据已有的数据表，对来自QQ空间的文本中的表情标识符（形如`[em]e123[/em]`）进行转换。QQ自带的表情将会转换为形如`[/微笑]`的形式（部分无名称的表情无法这么做），emoji表情将会转换为对应的emoji文字。

emoji的显示需要操作系统支持，并且由于版本更新，不一定所有的表情都可以被显示。

另外，一些数据库对emoji的支持不好。经验证，PostgreSQL、SQLite支持emoji，MySQL经修改编码为utf8mb4后也能够支持emoji。

即使数据库支持emoji，数据库操作工具也不一定支持。

QQ空间不支持所有的emoji，甚至会将某些emoji转为其他的emoji（已知`💆🏼‍♀️💆🏽‍♀️💆🏾‍♀️💆🏿‍♀️`会被转为`👹👺👻👼`；QQ空间不支持联合国的旗帜`🇺🇳`，与其接近的旗帜可能会受到影响，转为其他的旗帜和字母）。

```python
emotion_parse(content)
```

参数：

`content`：字符串类型，解析前的文本。

函数会返回一个字符串类型的数据，表示解析后的文本。

### `fine_json_parse`

对QQ空间动态的细JSON数据进行，取有用的数据重新组合。

```python
rough_json_parse(rough_json_list, ordernum, fine_json, catch_time=0)
```

参数：

1. `rough_json_list`：列表类型，爬取的动态的粗JSON数据的Python表达方式。
2. `ordernum`：整数类型，`rough_json_list`中的列表编号，代表其中的某一条动态的编号。
3. `fine_json`：字典类型，爬取的动态的细JSON数据的Python表达方式。
4. `catch_time`：整数类型，爬取数据时的时间戳。默认值为0。建议使用细JSON的爬取时间。

函数会返回一个字典类型的数据，表示解析后的动态的细数据的JSON的Python表达方式。

### `db_init`

对数据库进行初始化。

需要另外导入数据库相关的模块。

```python
db_init()
```

无参数，无返回值。

### `db_write_rough`

向数据库中写入粗数据。

需要另外导入数据库相关的模块。

```python
db_write_rough(parse)
```

参数：

`parse`：字典类型，解析后的动态的粗数据的JSON的Python表达方式。

无返回值。

### `db_write_fine`

向数据库中写入细数据。

需要另外导入数据库相关的模块。

```python
db_write_fine(parse)
```

参数：

`parse`：字典类型，解析后的动态的细数据的JSON的Python表达方式。

无返回值。

## 许可

由于软件著作权的关系，许可

### 使用到的组件

Python使用PSF LICENSE。

Requests使用Apache License, Version 2.0

Selenium使用Apache License, Version 2.0。