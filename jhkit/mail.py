#! /usr/bin/env python3

'''
# 模块名称：hmail
# 模块版本：v1.0.6
# 功能描述：
 - 支持邮件发送
# 重要版本变更说明：
 - To/Cc/Bcc的列表拼接采用逗号的形式拼接，原因是原来采用多个To/Cc/Bcc会导致
   在某些邮件客户端上只显示一个To/Cc/Bcc内容.
   比如：Header里面内容如：
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   这样只会显示一个huj，
   现在修改变成：
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>,=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   这样就可以显示出2个huj，huj了
Date:2019-06-27
Author:J.Hu
'''

# smtplib   负责发送邮件
# email     负责构造邮件
from smtplib import SMTP,SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formataddr
from email.header import Header

# 邮件格式类型
TYPE_PLAIN      = 'plain'
TYPE_HTML       = 'html'
TYPE_BASE64     = 'base64'
TYPE_LIST = (
    TYPE_PLAIN,
    TYPE_HTML,
    TYPE_BASE64
)

# 邮件内容编码类型
ENCODE_UTF8 = 'utf-8'
ENCODE_LIST = (
    ENCODE_UTF8
)

# 收发信人类型
SENDTYPE_FROM   = 'From'
RECVTYPE_TO     = 'To'
RECVTYPE_CC     = 'Cc'
RECVTYPE_BCC    = 'Bcc'


class JHcontact:
    """
    联系人类型
    """
    def __init__(self, addr, name=None):
        if not isinstance(addr,str):raise TypeError(f'str TypeErr:{addr}')
        self.addr = str(addr)
        self.name = name or addr

class JHattach:
    """
    附件类型
    """
    def __init__(self,path,name=None):
        if not isinstance(path,str):raise TypeError(path)
        self.path = path
        self.name = name or path.split('/')[-1]

class JHsmtp:
    """
    SMTP业务封装实现
    """
    def __init__(self,user,pwd,host,port=465,ssl=True,timeout=5):
        """
        初始化并连接登陆服务器
        Params:
            - user:用户名
            - pwd:密码
            - host：服务器名
            - port：服务器端口，默认465
            - ssl：是否启用SSL(True：启用 / False：不启用) default:True
            - timeout:连接超时时间，默认5s
        """
        # 初始化数据
        self.__contact = {SENDTYPE_FROM:[],RECVTYPE_TO:[],RECVTYPE_CC:[],RECVTYPE_BCC:[]}

        # 连接服务器
        smtpfunc = SMTP_SSL if ssl else SMTP
        self.__obj = smtpfunc(host,port,timeout = timeout)
        self.__obj.login(user,pwd)
        self.from_set(user,user)

    def from_set(self,addr,name):
        self.__contact_set(SENDTYPE_FROM,[(addr,name)])

    def to_set(self,pairlst):
        self.__contact_set(RECVTYPE_TO,pairlst)

    def cc_set(self,pairlst):
        self.__contact_set(RECVTYPE_CC,pairlst)

    def bcc_set(self,pairlst):
        self.__contact_set(RECVTYPE_BCC,pairlst)

    def __contact_set(self,type,pairlst):
        '''
        联系人设置
        '''
        lst = []
        for(addr,name) in pairlst:
            lst.append(JHcontact(addr,name))
        self.__contact[type] = lst

    def __param_chk(self,val,lst):
        if val not in lst:
            raise ValueError(f'Input Value:[{val}] not in {lst}')

    def send(self,title,msg,att_lst=[],type=TYPE_HTML,encode=ENCODE_UTF8):
        """
        # 发送邮件
        """
        self.__param_chk(type,TYPE_LIST)
        self.__param_chk(encode,ENCODE_LIST)

        mime = MIMEMultipart()

        # 设置Title
        mime['Subject'] = Header(title,encode)
        # 设置联系人
        for k in self.__contact.keys():
            contact_str = ''
            for item in self.__contact[k]:
                catflg = ',' if contact_str else ''
                contact_str = f'{contact_str}{catflg}{formataddr([item.name,item.addr])}'
            mime[k] = contact_str

        # 设置正文内容
        mime.attach(MIMEText(msg,type,encode))

        # 设置附件
        def mime_attach(mime, att, attid, encode):
            li = JHattach(att)
            att = MIMEText(open(li.path,'rb').read(), TYPE_BASE64, encode)
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename='+li.name
            att.add_header('Content-ID', str(attid))
            mime.attach(att)

        # 添加附件
        attid = 0
        for li in att_lst:
            mime_attach(mime,li,attid,encode)
            attid += 1

        # 发件人邮件和收件人邮件地址的设定
        from_addr = self.__contact[SENDTYPE_FROM][0].addr
        to_addrs = []
        for val in [RECVTYPE_TO,RECVTYPE_CC,RECVTYPE_BCC]:
            for contact in self.__contact[val]:
                to_addrs.append(contact.addr)

        #发送邮件
        self.__obj.sendmail(from_addr, to_addrs, mime.as_string())

    def close(self):
        """
        关闭连接
        """
        self.__obj.quit()


if __name__ == '__main__':
    # Template for hmail SMTP
    '''
    HOST = 'smtp.exmail.qq.com'
    smtp = JHsmtp(USER,PWD,HOST)
    smtp.from_set(USER,'FromName')
    smtp.to_set([('cantahu@163.com','ToName-1'),('joestarhu@163.com','ToName-2')])
    smtp.cc_set([('cantahu@163.com','CcName-1'),('joestarhu@163.com','CcName-2')])
    smtp.bcc_set([('cantahu@163.com','BccName-1'),('joestarhu@163.com','BccName-2')])
    # 附件在邮件中以图片形式显示可以用HTMLCode
    # <img src="cid:0"/> cid：0 代表附件ID为0的附件，需要自己拼装
    try:
        smtp.send('邮件标题','邮件正文内容',['mail.py'])
    except Exception as e:
        print(e)
    smtp.close()
    '''
