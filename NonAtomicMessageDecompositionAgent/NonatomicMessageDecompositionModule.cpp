/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "NonAtomicMessageDecompositionModule.hpp"

SC_IMPLEMENT_MODULE(NonAtomicMessageDecompositionModule)

sc_result NonAtomicMessageDecompositionModule::InitializeImpl()
{
  m_NonAtomicMessageDecompositionService.reset(new NonAtomicMessageDecompositionPythonService("NonAtomicMessageDecompositionAgent/NonAtomicMessageDecompositionModule.py"));
  m_NonAtomicMessageDecompositionService->Run();
  return SC_RESULT_OK;
}

sc_result NonAtomicMessageDecompositionModule::ShutdownImpl()
{
  m_NonAtomicMessageDecompositionService->Stop();
  m_NonAtomicMessageDecompositionService.reset();
  return SC_RESULT_OK;
}
