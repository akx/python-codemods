import inspect
import re
from textwrap import indent
from typing import Sequence, List, Optional

import libcst as cst
from libcst.codemod import VisitorBasedCodemodCommand

TYPELINE_RE = re.compile(r"^\s*:type\s*(.+?)\s*:\s*(.+?)\s*$")
RTYPELINE_RE = re.compile(r"^\s*:rtype\s*:\s*(.+?)\s*$")
RETURN = "$RETURN$"


def update_parameters(
    params: cst.Parameters,
    get_annotation,
    overwrite_existing_annotations: bool,
) -> cst.Parameters:
    def update_annotation(
        parameters: Sequence[cst.Param],
    ) -> List[cst.Param]:
        annotated_parameters = []
        for parameter in parameters:
            # key = parameter.name.value
            anno = get_annotation(parameter)
            if anno and (overwrite_existing_annotations or not parameter.annotation):
                parameter = parameter.with_changes(annotation=anno)
            annotated_parameters.append(parameter)
        return annotated_parameters

    return params.with_changes(
        params=update_annotation(
            params.params,
        ),
        kwonly_params=update_annotation(
            params.kwonly_params,
        ),
        posonly_params=update_annotation(
            params.posonly_params,
        ),
    )


def gather_types(docstring):
    types = {}
    new_docstring_lines = []
    for line in docstring.splitlines():
        m = TYPELINE_RE.match(line.strip())
        if m:
            types[m.group(1)] = m.group(2)
            continue
        m = RTYPELINE_RE.match(line.strip())
        if m:
            types[RETURN] = m.group(1)
            continue
        new_docstring_lines.append(line)
    return ("\n".join(new_docstring_lines), types)


def get_docstring_node(
    body,
) -> cst.Expr:
    if isinstance(body, Sequence):
        if body:
            expr = body[0]
        else:
            return None
    else:
        expr = body
    while isinstance(expr, (cst.BaseSuite, cst.SimpleStatementLine)):
        if len(expr.body) == 0:
            return None
        expr = expr.body[0]
    if not isinstance(expr, cst.Expr):
        return None
    return expr


class RtypeCodemodCommand(VisitorBasedCodemodCommand):
    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        docstring = None
        docstring_node = get_docstring_node(updated_node.body)
        if docstring_node:
            if isinstance(
                docstring_node.value, (cst.SimpleString, cst.ConcatenatedString)
            ):
                docstring = docstring_node.value.evaluated_value
        if not docstring:
            return updated_node
        new_docstring, types = gather_types(docstring)
        if types.get(RETURN):
            updated_node = updated_node.with_changes(
                returns=cst.Annotation(cst.Name(types.pop(RETURN))),
            )

        if types:

            def get_annotation(p: cst.Param) -> Optional[cst.Annotation]:
                pname = p.name.value
                if types.get(pname):
                    return cst.Annotation(cst.parse_expression(types[pname]))
                return None

            updated_node = updated_node.with_changes(
                params=update_parameters(updated_node.params, get_annotation, False)
            )

        new_docstring_node = cst.SimpleString('"""%s"""' % new_docstring)
        return updated_node.deep_replace(docstring_node, cst.Expr(new_docstring_node))
