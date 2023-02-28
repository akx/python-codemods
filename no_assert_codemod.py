import libcst as cst
from libcst.codemod import VisitorBasedCodemodCommand


def _get_assert_replacement(node: cst.Assert):
    if node.msg:
        message = node.msg
    else:
        message = cst.SimpleString(value=repr(str(cst.Module(body=[node]).code)))
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
                                    cst.Arg(value=message),
                                ],
                            ),
                        ),
                    ]
                ),
            ],
        ),
    )


class RewriteAssertToIfRaise(VisitorBasedCodemodCommand):
    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine:
        if isinstance(updated_node.body[0], cst.Assert):
            if_stmt = _get_assert_replacement(updated_node.body[0])
            replacement = updated_node.deep_replace(updated_node, if_stmt)
            return replacement
        return updated_node
