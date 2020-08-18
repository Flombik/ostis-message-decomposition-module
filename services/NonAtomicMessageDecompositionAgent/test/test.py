from NonAtomicMessageDecompositionAgent.NonAtomicMessageDecompositionAgent import text_decomposition, NonAtomicMessageDecompositionAgent
from unittest import defaultTestLoader, TestLoader, TestCase, TextTestRunner

from common import *
from sc import *

module = None

class TestTextDecomposition(TestCase):
    def test_text_decomposition(self):
        text = 'Ехал грека через реку, видит грека — в реке рак. Сунул грека руку в реку, рак за руку греку — цап!'
        self.assertEqual(text_decomposition(text, lang='ru'), [
                         'Ехал грека через реку, видит грека — в реке рак.', 'Сунул грека руку в реку, рак за руку греку — цап!'])


class TestAgentMethods(TestCase):
    def test_link_finding(self):
        pass

    def test_gen_tuple(self):
        pass

    def test_gen_submessages(self):
        pass

    def test_agent(self):
        action_addr = self.ctx.HelperResolveSystemIdtf(
            "action_nonatomic_message_decomposition", ScType.NodeConstClass)

        agent = NonAtomicMessageDecompositionAgent(Module())
        agent.Register(action_addr, ScPythonEventType.AddOutputEdge)

        nrel_sc_text_translation_addr = self.ctx.HelperResolveSystemIdtf(
            'nrel_sc_text_translation', ScType.NodeConstNoRole)
        concept_message_addr = self.ctx.HelperResolveSystemIdtf(
            'concept_message', ScType.NodeConstClass)
        nrel_authors_addr = self.ctx.HelperResolveSystemIdtf(
            'nrel_authors', ScType.NodeConstNoRole)

        templ = ScTemplate()
        templ.TripleWithRelation(
            ScType.NodeVar >> '_message_name',
            ScType.EdgeDCommonVar,
            ScType.NodeVar >> '_message_author',
            ScType.EdgeAccessVarPosPerm,
            nrel_authors_addr
        )
        templ.TripleWithRelation(
            ScType.NodeVar >> '_temp',
            ScType.EdgeDCommonVar,
            '_message_name',
            ScType.EdgeAccessVarPosPerm,
            nrel_sc_text_translation_addr
        )
        templ.Triple(
            '_temp',
            ScType.EdgeAccessVarPosPerm,
            ScType.LinkVar >> '_text'
        )
        templ.Triple(
            concept_message_addr,
            ScType.EdgeAccessVarPosPerm,
            '_message_name'
        )
        templ.Triple(
            ScType.NodeVar >> '_action_node',
            ScType.EdgeAccessVarPosPerm,
            '_message_name'
        )
        lang_de_addr = self.ctx.HelperResolveSystemIdtf(
            "lang_de", ScType.NodeConst)
        templ.Triple(
            lang_de_addr,
            ScType.EdgeAccessVarPosPerm,
            '_text'
        )

        params = ScTemplateParams()

        new_message_node_addr = self.ctx.CreateNode(ScType.NodeConst)
        self.ctx.HelperSetSystemIdtf(
            'recognised_message', new_message_node_addr)
        params.Add('_message_name', new_message_node_addr)

        message_author_node_addr = self.ctx.CreateNode(ScType.NodeConst)
        self.ctx.HelperSetSystemIdtf(
            'speech_recognition_module', message_author_node_addr)
        params.Add('_message_author', message_author_node_addr)

        text = "Jeder hat das Recht auf Bildung. \
            Die Bildung ist unentgeltlich, zum mindesten der Grundschulunterricht und die grundlegende Bildung. \
            Der Grundschulunterricht ist obligatorisch. \
            Fach- und Berufsschulunterricht müssen allgemein verfügbar gemacht werden, \
            und der Hochschulunterricht muß allen gleichermaßen entsprechend ihren Fähigkeiten offenstehen."
        link_addr = self.ctx.CreateLink()
        self.ctx.SetLinkContent(link_addr, text)
        params.Add('_text', link_addr)

        result = self.ctx.HelperGenTemplate(templ, params)

        temp_edge_addr = self.ctx.CreateEdge(
            ScType.EdgeAccessConstPosPerm, action_addr, result['_action_node'])


def MemoryCtx() -> ScMemoryContext:
    return __ctx__

def Module() -> ScMoudle:
    return module

def RunTests():
    global TestLoader, TextTestRunner

    tests = [
        TestTextDecomposition,
        TestAgentMethods,
    ]

    for testItem in tests:
        testItem.MemoryCtx = MemoryCtx
        testItem.Module = Module
        suite = defaultTestLoader.loadTestsFromTestCase(testItem)
        res = TextTestRunner(verbosity=2).run(suite)
        if not res.wasSuccessful():
            raise Exception("Unit test failed")


class TestModule(ScModule):
    def __init__(self):
        ScModule.__init__(self,
                          ctx=__ctx__,
                          cpp_bridge=__cpp_bridge__,
                          keynodes=[
                          ])

    def DoTests(self):
        try:
            RunTests()
        except Exception as ex:
            raise ex
        except:
            print("Unexpected error")
        finally:
            module.Stop()

    def OnInitialize(self, params):
        self.DoTests()

    def OnShutdown(self):
        pass


module = TestModule()
module.Run()
