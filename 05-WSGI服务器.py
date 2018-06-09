import socket
import re
import multiprocessing
import time
import dynamic.web_frame05


class MINIweb(object):
    def __init__(self):
        # 1. 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2. 绑定
        self.tcp_server_socket.bind(("", 7890))

        # 3. 变为监听套接字
        self.tcp_server_socket.listen(128)

    def service_client(self, new_socket):
        """为这个客户端返回数据"""

        # 1. 接收浏览器发送过来的请求 ，即http请求
        # GET / HTTP/1.1
        # .....
        request = new_socket.recv(1024).decode("utf-8")
        # print(">>>"*50)
        # print(request)

        request_lines = request.splitlines()
        print("")
        print(">" * 20)
        print(request_lines)

        # /add/000007.html  ==> file_name
        # GET /index.html HTTP/1.1
        # get post put del
        file_name = ""
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        if ret:
            file_name = ret.group(1)
            # print("*"*50, file_name)
            if file_name == "/":
                file_name = "/index.html"

        # 2. 返回http格式的数据，给浏览器

        if not file_name.endswith(".html"):  # 不是以py结尾的文件,我们认为是静态资源
            # 返回静态资源
            try:
                f = open("./static" + file_name, "rb")
            except:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "------file not found-----"
                new_socket.send(response.encode("utf-8"))
            else:
                html_content = f.read()
                f.close()
                # 2.1 准备发送给浏览器的数据---header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 2.2 准备发送给浏览器的数据---body
                # response += "hahahhah"

                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将response body发送给浏览器
                new_socket.send(html_content)
        else:
            # 动态资源
            env = {}
            env["PATH_NAME"] = file_name
            # {"PATH_NAME":"index.py"}
            body = dynamic.web_frame05.application(env, self.func)

            header = "HTTP/1.1 %s\r\n" % self.statues

            for i in self.headers:
                header += "%s:%s\r\n" % (i[0], i[1])

            header += "\r\n"

            response = header + body

            new_socket.send(response.encode("utf-8"))

        # 关闭套接
        new_socket.close()

    def func(self, statues, headers):
        self.statues = statues
        self.headers = [("Sever", "1.1")]
        self.headers += headers

    def runforever(self):
        """用来完成整体的控制"""

        while True:
            # 4. 等待新客户端的链接
            new_socket, client_addr = self.tcp_server_socket.accept()

            # 5. 为这个客户端服务
            p = multiprocessing.Process(target=self.service_client, args=(new_socket,))
            p.start()

            new_socket.close()

        # 关闭监听套接字
        tcp_server_socket.close()


# 开启服务器
def main():
    mini_web = MINIweb()
    mini_web.runforever()


if __name__ == "__main__":
    main()
