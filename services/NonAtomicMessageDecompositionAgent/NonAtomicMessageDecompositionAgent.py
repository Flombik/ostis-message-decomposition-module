from common import ScModule, ScAgent, ScEventParams
from sc import *

try:
    import spacy
    from spacy.lang.ru import Russian
except AttributeError:
    import sys
    if not hasattr(sys, 'argv'):
        sys.argv = ['']
    import spacy
    from spacy.lang.ru import Russian


def text_decomposition(text, lang='de'):
    if lang == 'de':
        nlp = spacy.load('de_core_news_md')
    elif lang == 'en':
        nlp = spacy.load("en_core_web_md")
    elif lang == 'ru':
        nlp = Russian()
        sentencizer = nlp.create_pipe("sentencizer")
        nlp.add_pipe(sentencizer)
    else:
        print("Unsupported language. Choose from ['en', 'de', 'ru']")
        return

    doc = nlp(text)
    sentences = list()
    for sent in doc.sents:
        sentences.append(sent.text)
    return sentences


class NonAtomicMessageDecompositionAgent(ScAgent):
    def __init__(self, module):
        super().__init__(module)
        self.answer = None

    def RunImpl(self, evt: ScEventParams) -> ScResult:
        search_result = self.findStructure(evt.other_addr)
        if search_result.Size() != 1:
            return ScResult.ErrorInvalidParams

        search_item = search_result[0]

        link_index = search_result.Aliases()['_text']
        text = self.module.ctx.GetLinkContent(
            search_item[link_index]).AsString()

        message_index = search_result.Aliases()['_message']
        message_node_addr = search_item[message_index]

        lang_index = search_result.Aliases()['_lang']
        lang_node_addr = search_item[lang_index]
        lang = self.module.ctx.HelperGetSystemIdtf(lang_node_addr)[5:]

        self.genSubmessages(text_decomposition(
            text, lang=lang), self.genTupleNode(message_node_addr))

        self.finishAgentWork(evt.other_addr)
        return ScResult.Ok

    def finishAgentWork(self, questionNode, isSuccess=True):
        question_finished_addr = self.module.ctx.HelperResolveSystemIdtf(
            'question_finished', ScType.Unknown)

        self.module.ctx.CreateEdge(
            ScType.EdgeAccessConstPosPerm, question_finished_addr, questionNode)
        if isSuccess:
            status_node_addr = self.module.ctx.HelperResolveSystemIdtf(
                'question_finished_successfully', ScType.Unknown)
        else:
            status_node_addr = self.module.ctx.HelperResolveSystemIdtf(
                'question_finished_unsuccessfully', ScType.Unknown)
        self.module.ctx.CreateEdge(
            ScType.EdgeAccessConstPosPerm, status_node_addr, questionNode)

    def findStructure(self, question_node):
        nrel_sc_text_translation_addr = self.module.ctx.HelperResolveSystemIdtf(
            'nrel_sc_text_translation', ScType.NodeConstNoRole)
        concept_message_addr = self.module.ctx.HelperResolveSystemIdtf(
            'concept_message', ScType.NodeConstClass)

        link_with_text_search_templ = ScTemplate()
        link_with_text_search_templ.Triple(
            question_node,
            ScType.EdgeAccessVarPosPerm,
            ScType.NodeVar >> '_message'
        )
        link_with_text_search_templ.TripleWithRelation(
            ScType.NodeVar >> '_temp',
            ScType.EdgeDCommonVar,
            '_message',
            ScType.EdgeAccessVarPosPerm,
            nrel_sc_text_translation_addr
        )
        link_with_text_search_templ.Triple(
            '_temp',
            ScType.EdgeAccessVarPosPerm,
            ScType.LinkVar >> '_text'
        )
        link_with_text_search_templ.Triple(
            concept_message_addr,
            ScType.EdgeAccessVarPosPerm,
            '_message'
        )
        link_with_text_search_templ.Triple(
            ScType.NodeVar >> '_lang',
            ScType.EdgeAccessVarPosPerm,
            '_text'
        )

        return self.module.ctx.HelperSearchTemplate(link_with_text_search_templ)

    def genTupleNode(self, message_addr):
        nrel_message_decomposition_addr = self.module.ctx.HelperResolveSystemIdtf(
            'nrel_message_decomposition', ScType.NodeConstNoRole)

        tuple_node_addr = self.module.ctx.CreateNode(ScType.NodeConstTuple)

        tuple_templ = ScTemplate()
        tuple_templ.TripleWithRelation(
            ScType.NodeVarTuple >> '_tuple',
            ScType.EdgeDCommonVar,
            ScType.NodeVar >> '_message',
            ScType.EdgeAccessVarPosPerm,
            ScType.NodeVarNoRole >> '_nrel'
        )
        params = ScTemplateParams()
        params.Add('_tuple', tuple_node_addr)
        params.Add('_message', message_addr)
        params.Add('_nrel', nrel_message_decomposition_addr)
        self.module.ctx.HelperGenTemplate(tuple_templ, params)

        return tuple_node_addr

    def genSubmessages(self, messages, tuple_addr):
        nrel_sc_text_translation_addr = self.module.ctx.HelperResolveSystemIdtf(
            'nrel_sc_text_translation', ScType.NodeConstNoRole)
        concept_atomic_message_addr = self.module.ctx.HelperResolveSystemIdtf(
            'concept_atomic_message', ScType.NodeConstClass)
        nrel_message_sequence_addr = self.module.ctx.HelperResolveSystemIdtf(
            'nrel_message_sequence', ScType.NodeConstNoRole)

        sc_text_translation_templ = ScTemplate()
        sc_text_translation_templ.Triple(
            ScType.NodeVarClass >> '_class',
            ScType.EdgeAccessVarPosPerm,
            ScType.NodeVar >> '_message'
        )
        sc_text_translation_templ.TripleWithRelation(
            ScType.NodeVar >> '_temp',
            ScType.EdgeDCommonVar,
            '_message',
            ScType.EdgeAccessVarPosPerm,
            nrel_sc_text_translation_addr
        )
        sc_text_translation_templ.Triple(
            '_temp',
            ScType.EdgeAccessVarPosPerm,
            ScType.LinkVar >> '_text'
        )

        prev_atom_msg_addr = None
        for index, sentence in enumerate(messages):
            atom_message_node_addr = self.module.ctx.CreateNode(
                ScType.NodeConst)
            self.module.ctx.HelperSetSystemIdtf(
                'sub_message_{}'.format(index+1), atom_message_node_addr)

            atom_message_params = ScTemplateParams()
            atom_message_params.Add('_class', concept_atomic_message_addr)
            atom_message_params.Add('_message', atom_message_node_addr)
            sentence_link = self.module.ctx.CreateLink()
            self.module.ctx.SetLinkContent(sentence_link, sentence)
            atom_message_params.Add('_text', sentence_link)
            self.module.ctx.HelperGenTemplate(
                sc_text_translation_templ, atom_message_params)

            tpl_msg_edge_addr = self.module.ctx.CreateEdge(
                ScType.EdgeAccessConstPosPerm, tuple_addr, atom_message_node_addr)

            if prev_atom_msg_addr is None:
                rrel_1_addr = self.module.ctx.HelperResolveSystemIdtf(
                    'rrel_1', ScType.NodeConstRole)
                self.module.ctx.CreateEdge(
                    ScType.EdgeAccessConstPosPerm, rrel_1_addr, tpl_msg_edge_addr)
            else:
                next_msg_edge_addr = self.module.ctx.CreateEdge(
                    ScType.EdgeDCommonConst, prev_atom_msg_addr, atom_message_node_addr)
                self.module.ctx.CreateEdge(
                    ScType.EdgeAccessConstPosPerm, nrel_message_sequence_addr, next_msg_edge_addr)

            prev_atom_msg_addr = atom_message_node_addr
