html:
    head:  ## line comment
        #:
            block comment
            comment again
    body:
        .container.row.span12#content data-url=/static/login:
            form.form.form-horizontal#login-form action=/accounts/login,
                    method=post, data-action=add:
                a.btn.btn-primary href=/signin:
                    span.label:
                        b:
                            -数目@count
                    span.content:
                        -内容@content
                :text autofocus, required, placeholder=用户名, value=@username
                :text.btn.btn-danger#login-btn value=登录
                .trucks:

                    @for truck in trucks:
                        -司机姓名@truck.owner.name
                        -车牌号码@truck.plate_number

                    @def hello(words):
                        @for w in words:
                            p.title:
                                -hello @{w + a}

                    @words = ['how', 'do', 'you', 'do', '?']
                    @hello(words)

                    @words2 = [len(i) for i in words]
                    @label = 'valid' if valid else 'invalid'

                    @import json
                    @html = json.dumps(words2)
