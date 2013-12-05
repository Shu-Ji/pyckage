
        @name
    ~~~~~~~~~~~~~~~~~
    @{import re}
    @{my_name = 'hyson'}
    @{
        r = re.compile(r'\d+')
        @:output variable @r.sub('_','Hello12345art321mustache')!@#$%^&*()_+
        def say_hello(name):
            return 'hello'+str(name)
    }
    @def fun(name){
        @{
            s = 'hello ' + str(name)
            def fun2(vars):
                return '<b>'+str(vars)+'</b>'
        }
        <h1>@name</h1>
        <h1>@s</h1>
        <h1>@fun2(name)</h1>
    }
    @for i in numbers{
        <li>line @i</li>
        @{fun(i)}
    }
    @say_hello(my_name)
    @say_hello('world')
    <span> span</span>

