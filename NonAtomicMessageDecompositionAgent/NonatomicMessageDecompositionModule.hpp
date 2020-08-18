/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/


#pragma once

#include "sc-memory/sc_module.hpp"
#include "NonAtomicMessageDecompositionService.hpp"
#include "NonAtomicMessageDecompositionModule.generated.hpp"


class NonAtomicMessageDecompositionModule : public ScModule
{
  SC_CLASS(LoadOrder(999))
  SC_GENERATED_BODY()

  virtual sc_result InitializeImpl() override;
  virtual sc_result ShutdownImpl() override;

private:
  std::unique_ptr<NonAtomicMessageDecompositionPythonService> m_NonAtomicMessageDecompositionService;
};
