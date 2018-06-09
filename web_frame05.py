import re
import urllib.parse  # 注意
import logging
from pymysql import connect

"""
FUNC_URL_DICT = {
    "/index.html":index,  # 127.0.0.1/index.html
    "/center.html":center
}
FUNC_URL_DICT["/index.py"] = index
FUNC_URL_DICT["/center.py"] = center
"""
FUNC_URL_DICT = {}


# func ==> index  url ==>"/index.py"
def route(url):
    def func_out(func):
        FUNC_URL_DICT[url] = func

        def func_in(*args, **kwargs):
            return func()

        return func_in

    return func_out


@route(r"/index.html")
def index(ret):
    with open("./templates/index.html") as f:
        content = f.read()
    # 链接
    db = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                 charset='utf8')
    # 游标
    cursor = db.cursor()
    # 执行sql语句
    sql = "select * from info;"
    cursor.execute(sql)
    # 取数据
    # ((),(),())
    my_stock = cursor.fetchall()
    # 关闭
    cursor.close()
    db.close()

    html_temp = """<tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule=%s>
        </td>
        </tr>"""

    html = ""
    for i in my_stock:
        html += html_temp % (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[1])

    content = re.sub(r"\{%content%\}", html, content)
    return content


@route(r"/center.html")
def center(ret):
    with open("./templates/center.html") as f:
        content = f.read()

    # 链接
    db = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                 charset='utf8')
    # 游标
    cursor = db.cursor()
    # 执行sql语句
    sql = "select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id = f.id;"
    cursor.execute(sql)
    # 取数据
    # ((),(),())
    my_stock = cursor.fetchall()
    # 关闭
    cursor.close()
    db.close()

    html_temp = """<tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>
                <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
            </td>
            <td>
                <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
            </td>
        </tr>"""

    html = ''
    for i in my_stock:
        html += html_temp % (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[0], i[0])

    content = re.sub(r"\{%content%\}", html, content)

    return content


@route(r"/del/(\d+)\.html")
def add_focus(ret):
    # 获取股票代码  000007
    stock_code = ret.group(1)

    # 链接
    db = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                 charset='utf8')
    # 游标
    cursor = db.cursor()

    # 1 检查股票是否存在 不存在直接返回错误
    sql = "select * from info where info.code = %s"
    cursor.execute(sql, stock_code)
    ret = cursor.fetchone()
    if not ret:
        cursor.close()
        db.close()
        return "没有这个股票。。。"

    # 2 检查是否已经关注 关注了直接返回错误
    sql = "select * from focus where focus.id = (select id from info where info.code = %s)"
    cursor.execute(sql, [stock_code])
    ret = cursor.fetchone()
    if not ret:
        cursor.close()
        db.close()
        return "没有关注这个股票。。。"

    # 3 添加股票信息
    # 执行sql语句
    sql = "delete from focus where focus.id = (select id from info where info.code = %s)"
    cursor.execute(sql, [stock_code])
    db.commit()
    cursor.close()
    db.close()

    return "del ok...%s" % stock_code


@route(r"/add/(\d+)\.html")
def add_focus(ret):
    # 获取股票代码  000007
    stock_code = ret.group(1)

    # 链接
    db = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                 charset='utf8')
    # 游标
    cursor = db.cursor()

    # 1 检查股票是否存在 不存在直接返回错误
    sql = "select * from info where info.code = %s"
    cursor.execute(sql, stock_code)
    ret = cursor.fetchone()
    if not ret:
        cursor.close()
        db.close()
        return "没有这个股票。。。"

    # 2 检查是否已经关注 关注了直接返回错误
    sql = "select * from focus where focus.id = (select id from info where info.code = %s)"
    cursor.execute(sql, [stock_code])
    ret = cursor.fetchone()
    if ret:
        cursor.close()
        db.close()
        return "已经关注过了。。。"

    # 3 添加股票信息
    # 执行sql语句
    sql = "insert into focus(id) select id from info where info.code = %s"
    cursor.execute(sql, [stock_code])
    db.commit()
    cursor.close()
    db.close()

    return "add ok...%s" % stock_code


# /update/000007.html
@route(r"/update/(\d+)\.html")
def show_update(ret):
    # 提取股票代码
    stock_code = ret.group(1)

    with open("./templates/update.html") as f:
        content = f.read()

    # 从数据库中提取股票信息
    # 1 链接数据库
    db = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                 charset='utf8')
    cursor = db.cursor()

    # 2 执行ｓｑｌ语句
    sql = "select note_info from focus where id = (select id from info where info.code = %s);"
    cursor.execute(sql, stock_code)
    ret = cursor.fetchone()

    # 3 获取股票的备注信息
    stock_content = ret[0]

    content = re.sub(r"\{%code%\}", stock_code, content)
    content = re.sub(r"\{%note_info%\}", stock_content, content)

    return content


# /update/000007/中国.html
@route(r"/update/(\d+)/(.*)\.html")
def save_change_update(ret):
    # 1 获取股票的代码
    stock_code = ret.group(1)
    stock_note_info = ret.group(2)  # 中国　编码＝＝＝》　％２０％３０

    # ｕｒｌ特殊符号解码
    stock_note_info = urllib.parse.unquote(stock_note_info)

    # 2　连接数据库
    db = connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                 charset='utf8')
    cursor = db.cursor()

    # 3 执行ｓｑｌ语句
    sql = "update focus set note_info = %s where id = (select id from info where info.code = %s);"
    cursor.execute(sql, [stock_note_info, stock_code])
    db.commit()

    return "%s　修改成功" % stock_code


# FUNC_URL_DICT = {
#     r"/index.html":index,  # 127.0.0.1/index.html
#     r"/center.html":center
#     r"/add/(\d+)\.html" : add_focus # 127.0.0.1:8080/add/000007.html
#     r"/del/(\d+)\.html" : del_focus # 127.0.0.1:8080/del/000007.html
#     r"/update/(\d+)\.html" : show_update # 127.0.0.1:8080/update/000007.html
#     r"/update/(\d+)/(.*)\.html" : save_change_update" # 127.0.0.1:8080/update/000007/nihao.html
# }
def application(env, func):
    # env["PAHT_NAME"] ==> "/index.py"
    file_name = env["PATH_NAME"]
    body = "hahaha"

    statues = "200 OK"
    headers = [('Content-Type', 'text/html; charset=utf-8')]

    func(statues, headers)
    # if file_name == "/index.py":
    #     return index()
    # elif file_name == "/center.py":
    #     return center()
    # else:
    #     return body
    logging.basicConfig(level=logging.DEBUG,
                        filename='./log.txt',
                        filemode='a',
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    logging.info('这是 %s' % file_name)
    try:
        # func = FUNC_URL_DICT[file_name]  # ==>
        # return func()
        for my_file_name, func in FUNC_URL_DICT.items():
            #    r"/add/(\d+)\.html"  /add/000007.html
            ret = re.match(my_file_name, file_name)
            if ret:
                return func(ret)
        else:
            logging.warning("没有对应的函数")
            return "404 %s not found.." % file_name

    except Exception as ret:
        return "产生异常 %s" % ret
