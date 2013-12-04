html:
    head:  # line comment
        #:
            block comment
        link src=/static/css/home.css
        style rel=stylesheet/less:
            html {
                font-size: 14px;
                body {
                    margin: 0 auto;
                }
            }
    body:
        .container.row.span12#content data-url=/static/login:
            form.form.form-horizontal#login-form action=/accounts/login,
                    method=post, data-action=add:
                a.btn.btn-primary href=/signin:
                    span.label:
                        b content=数目@count
                    span.content content=内容@content
                :text autofocus, required, placeholder=用户名, value=@username
                :text.btn.btn-danger#login-btn value=登录
                .trucks:
                    @for truck in trucks:
                        司机姓名@truck.owner.name
                        车牌号码@truck.plate_number
                    @set a = 45
                    @def hello(words):
                        @for w in words:
                            p.title:
                                hello @{w + a}
                    @hello(['how', 'do', 'you', 'do', '?'])
        script type=javascript:
            $(function(){
                alert(3);
            });
