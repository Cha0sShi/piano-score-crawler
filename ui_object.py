# -*- coding:utf-8 -*-


import os
import urllib
from threading import Thread
from tkinter import Button
from tkinter import END
from tkinter import Entry
from tkinter import Frame
from tkinter import Label
from tkinter import LabelFrame
from tkinter import NS
from tkinter import NSEW
from tkinter import RIGHT
from tkinter import Tk
from tkinter import Y
from tkinter import ttk
from webbrowser import open
import re
import tk

from get_score_data import get_scorelist_by_keyname, get_and_save_scoreImage_by_id


def thread_it(func, *args):
    """
    将函数打包进线程
    """
    # 创建
    t = Thread(target=func, args=args)
    # 守护
    t.setDaemon(True)
    # 启动
    t.start()


def handlerAdaptor(fun, *args, **kwargs):
    return lambda event: fun(event, *args, **kwargs)


class UIObject:

    def __init__(self):
        self.root = None
        self.vbar = None
        self.treeview = None
        self.jsonData = ""
        self.jsonData_keyword = ""

    def project_statement_show(self):
        open("https://github.com/Cha0sShi")

    def project_statement_get_focus(self, event):
        self.project_statement.config(fg="black", cursor="hand1")

    def project_statement_lose_focus(self, event):
        self.project_statement.config(fg="#FF0000")

    def center_window(self, root, w, h):
        """
        让窗口居于屏幕中央
        :param root: root
        :param w: 窗口宽度
        :param h: 窗口高度
        :return:
        """
        # 获取屏幕 宽、高
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()

        # 计算 x, y 位置
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        root.geometry('%dx%d+%d+%d' % (11*w/16, 2*h/3, x, y))

    def clear_tree(self, treeview):
        """
        清空表格
        """
        if treeview is not None:
            x = treeview.get_children()
            for item in x:
                treeview.delete(item)

    def add_tree(self, scorelist, treeview):
        """
        新增数据到表格
        """
        for score in scorelist:
            url = "https://www.everyonepiano.cn/Music-{}.html".format(score["MIMusicNO"])
            treeview.insert("", "end", values=(score["Title"], score["Times"], url))

    def keyboard_T_vote_keyword(self):
        """
        在搜索框中键入回车键后触发相应的事件
        :param event:
        :return:
        """
        thread_it(self.search_score_by_name)

    def search_score_by_name(self):
        """
        从关键字中搜索符合条件的影片信息
        """
        # 按钮设置为灰色状态
        self.clear_tree(self.treeview)  # 清空表格
        # self.T_vote_keyword['state'] = DISABLED
        self.btn_search_by_name['text'] = '正在努力搜索'
        scorelist = get_scorelist_by_keyname(self.text_keyword.get())
        print(scorelist)
        self.add_tree(scorelist, self.treeview)

    # else:
    #     messagebox.showinfo('提示', err_str[:1000])

    # 按钮设置为正常状态
    # self.C_type['state'] = 'readonly'
    # self.T_count['state'] = NORMAL

    # 下载按键

    def download(self):
        selected = self.treeview.focus()
        values = self.treeview.item(selected, 'values')
        url = values[2]
        pattern = r"-([0-9]+).html"
        match = re.search(pattern, url)
        scoreId = match.group(1)
        title = values[0]
        print(scoreId)
        def choose_type():
            selected_type = None

            def set_selected_type(scoretype_t):
                nonlocal selected_type
                selected_type = scoretype_t
                pop.quit()

            pop = Tk()

            # 创建选择Type的标签
            label = ttk.Label(pop, text="请选择Type:")
            label.pack()

            # 创建两个按钮，用于选择Type
            button_type1 = ttk.Button(pop, text="简谱", command=lambda: set_selected_type("Number"))
            button_type2 = ttk.Button(pop, text="五线谱", command=lambda: set_selected_type("Stave"))
            button_type1.pack()
            button_type2.pack()

            # 创建取消按钮
            button_cancel = ttk.Button(pop, text="取消", command=pop.quit)
            button_cancel.pack()

            pop.mainloop()
            pop.destroy()
            return selected_type

        scoretype = choose_type()
        if scoretype is not None:
            get_and_save_scoreImage_by_id(scoreId, title, scoretype)

    def ui_process(self):
        """
        Ui主程序
        :param
        :return:
        """
        root = Tk()
        self.root = root
        # 设置窗口位置
        root.title("Score Crawler")
        self.center_window(root, 1000, 565)
        # root.resizable(True, True)

        # 容器控件
        labelframe = LabelFrame(root, text="搜索乐谱")
        labelframe.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Add widgets or content inside the label frame

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self.labelframe = labelframe

        # 名称
        label_keyword = Label(labelframe, text='乐谱名称')
        label_keyword.place(x=0, y=15)
        self.label_keyword = label_keyword

        # 文本框
        text_keyword = Entry(labelframe, width=53)
        text_keyword.delete(0, END)
        text_keyword.insert(0, ' ')
        text_keyword.place(x=66, y=15)
        self.text_keyword = text_keyword

        # 查询按钮
        btn_search_by_name = Button(labelframe, text="根据名字搜索")
        btn_search_by_name.place(x=560, y=10)
        self.btn_search_by_name = btn_search_by_name

        # 框架布局，承载多个控件
        frame_root = Frame(labelframe, width=400)
        frame_list = Frame(frame_root)
        frame_scroll = Frame(frame_root)
        self.frame_root = frame_root
        self.frame_list = frame_list
        self.frame_scroll = frame_scroll

        # 表格初始化
        columns = ("乐谱名", "浏览次数", "网址")
        treeview = ttk.Treeview(frame_list, height=10, show="headings", columns=columns)
        treeview.column("乐谱名", width=210, anchor='center')
        treeview.column("浏览次数", width=210, anchor='center')
        treeview.column("网址", width=210, anchor='center')

        for col in columns:
            treeview.heading(col, text=col)

        # 垂直滚动条
        treeview = ttk.Treeview(frame_list, height=10, show="headings", columns=columns)
        # ... (configure columns and headings)

        # Create and configure the scrollbar
        treeScroll = ttk.Scrollbar(frame_list, orient="vertical")
        treeScroll.configure(command=treeview.yview)

        # Configure treeview to use the scrollbar
        treeview.configure(yscrollcommand=treeScroll.set)

        # Place both treeview and scrollbar in the frame
        treeview.grid(row=0, column=0, sticky="nsew")
        treeScroll.grid(row=0, column=1, sticky="ns")

        # 框架的位置布局
        frame_list.grid(row=0, column=0, sticky=NSEW)
        frame_scroll.grid(row=0, column=1, sticky=NS)
        frame_root.place(x=5, y=70)
        self.treeview=treeview
        # 下载键
        Button(root, text='下载', command=self.download).place(x=560, y=70)
        # 项目的一些信息
        # ft = font.Font(size=11, weight=font.BOLD)
        # project_statement = Label(root, text="项目地址", fg='#FF0000', font=ft, anchor=NW)
        # project_statement.place(x=5, y=540)
        # self.project_statement = project_statement

        # 绑定事件
        # treeview.bind('<Double-1>', self.open_in_browser_douban_url)  # 表格绑定鼠标左键事件
        # treeview_play_online.bind('<Double-1>', self.open_in_browser)  # 表格绑定左键双击事件
        # treeview_save_cloud_disk.bind('<Double-1>', self.open_in_browser_cloud_disk)  # 表格绑定左键双击事件
        # treeview_bt_download.bind('<Double-1>', self.open_in_browser_bt_download)  # 表格绑定左键双击事件
        btn_search_by_name.configure(command=lambda: thread_it(self.keyboard_T_vote_keyword))  # 按钮绑定单击事件
        # B_0_keyword.configure(command=lambda: thread_it(self.searh_movie_in_keyword))  # 按钮绑定单击事件
        # B_0_imdb.configure(command=lambda: thread_it(self.show_IDMB_rating))  # 按钮绑定单击事件
        text_keyword.bind('<Return>', handlerAdaptor(self.keyboard_T_vote_keyword))  # 文本框绑定选择事件
        # project_statement.bind('<ButtonPress-1>', self.project_statement_show)  # 标签绑定鼠标单击事件
        # project_statement.bind('<Enter>', self.project_statement_get_focus)  # 标签绑定获得焦点事件
        # project_statement.bind('<Leave>', self.project_statement_lose_focus)  # 标签绑定失去焦点事件

        root.mainloop()
