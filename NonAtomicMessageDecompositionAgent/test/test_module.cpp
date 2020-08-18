#include "sc-test-framework/sc_test_unit.hpp"
#include "sc-memory/python/sc_python_interp.hpp"
#include "sc-memory/python/sc_python_service.hpp"

#include "test_defines.hpp"

UNIT_TEST(MessageDecomposition)
{
    py::ScPythonInterpreter::AddModulesPath(SC_PS_PYTHON_PATH);
    SUBTEST_START("tests")
    {
        py::DummyService testService("NonAtomicMessageDecompositionAgent/test/test.py");
        testService.Run();

        while (testService.IsRun())
            std::this_thread::sleep_for(std::chrono::milliseconds(100));

        testService.Stop();
    }
    SUBTEST_END()
}

SC_AUTOMATION_TESTS("MessageDecompositionModule-tests")