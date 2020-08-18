from common import ScModule
from NonAtomicMessageDecompositionAgent import NonAtomicMessageDecompositionAgent

from sc import *


class NonAtomicMessageDecompositionModule(ScModule):

    def __init__(self):
        ScModule.__init__(
            self,
            ctx=__ctx__,
            cpp_bridge=__cpp_bridge__,
            keynodes=[
            ],
        )

    def OnInitialize(self, params):
        print('Initialize Message Decomposition module')
        action_addr = self.ctx.HelperResolveSystemIdtf(
            "action_nonatomic_message_decomposition", ScType.NodeConstClass)

        agent = NonAtomicMessageDecompositionAgent(self)
        agent.Register(action_addr, ScPythonEventType.AddOutputEdge)


    def OnShutdown(self):
        print('Shutting down Message Decomposition module')


service = NonAtomicMessageDecompositionModule()
service.Run()
