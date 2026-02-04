Define custom ``Executable``
############################

这篇教程会教你如何定义一个``Executable``. ``Executable`` is the part to interact with external resources 
(for example, external programs, datasets, etc.) in ``wrfrun``, :class:`GeoGrid <wrfrun.model.wrf.core.GeoGrid>`就属于``Executable``.
定义了一个``Executable``, 我们就相当于定义了如何处理一个外部程序的输入、运行和输出，这样``wrfrun``就能精确的控制外部程序的运行，并且还能通过``replay``功能
记录和重放该``Executable``的运行。

背景
****

在``wrfrun``中，所有的``Executable``都继承自同一个父类``ExecutableBase``。在进行类的初始化时，你必须向这个父类提供以下三个参数：``name``, ``cmd``, ``work_path``。

* ``name``：一个字符串，用于向``wrfrun``标识这个``Executable``的独一无二的名称。
* ``cmd``: 一个字符串或者一个包含字符串的列表，里面是需要执行的外部命令和相应的参数。
* ``work_path``: 执行相应的外部命令时，``wrfrun``的工作路径。

除此之外，``ExecutableBase``还接受三个关键字参数：

* ``mpi_use``: 布尔值，是否使用mpi，默认为``False``。
* ``mpi_cmd``: 字符串，mpi的命令，一般为``mpirun``.
* ``mpi_core_num``: 使用mpi运行程序时分配的CPU核数。

在本教程中我们先暂时忽略后面这三个参数，因为我们假定在为一个简单的外部脚本``test.py``定义``Executable``，其中的内容很简单, 从``input.txt``读取内容，
然后依次向``output.txt``中分别写入``Hello from output!``和读取的内容：

.. code-block:: python
    :caption: test.py

    with open("input.txt", "r") as f1:
        with open("output.txt", "w") as f2:

            f2.write("Hello from output!\n")
            f2.write(f1.read())

``input.txt``内容为

.. code-block:: text
    :caption: input.txt

    Hello from input!

类初始化的定义
**************

我们先继承父类``ExecutableBase``，然后进行必要的初始化. 如果你不知道``work_path``应该设置为什么，可以使用``wrfrun``内部定义好的临时工作路径``WRFRUN.config.WRFRUN_TEMP_PATH``。

.. code-block:: python
    :caption: main.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class Test(ExecutableBase):
        def __init__(self):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)
