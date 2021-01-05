from typing import Optional

from fixit import CstLintRule
import libcst as cst


class AvoidAsserts(CstLintRule):
    MESSAGE = "Asserts must not be used"

    def should_skip_file(self) -> bool:
        pth = str(self.context.file_path)
        return "tests" in pth

    def visit_SimpleStatementLine(self, node: "SimpleStatementLine") -> Optional[bool]:
        if isinstance(node.body[0], cst.Assert):
            if_stmt = self._get_assert_replacement(node.body[0])
            replacement = node.deep_replace(node, if_stmt)
            self.report(node, replacement=replacement)
        return super().visit_SimpleStatementLine(node)

    def _get_assert_replacement(self, node: cst.Assert):
        message = node.msg or str(cst.Module(body=[node]).code)
        return cst.If(
            test=cst.UnaryOperation(
                operator=cst.Not(),
                expression=node.test,  # Todo: parenthesize?
            ),
            body=cst.IndentedBlock(
                body=[
                    cst.SimpleStatementLine(
                        body=[
                            cst.Raise(
                                exc=cst.Call(
                                    func=cst.Name(
                                        value="AssertionError",
                                    ),
                                    args=[
                                        cst.Arg(
                                            value=cst.SimpleString(
                                                value=repr(message),
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                        ]
                    ),
                ],
            ),
        )
