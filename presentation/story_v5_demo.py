"""Explicit fictional authoring requests; application runtime does not import this."""
import json

COMMANDS={
 'create':{'tab':'objects','input':'新增一个对象：王工，测试负责人。他说话直接，重视验证记录和异常闭环。','result':'新建对象'},
 'edit':{'tab':'objects','input':'我觉得朱总更关注验证边界。他今天说：“条件没验证，就先别承诺交付。”帮我补充到画像和语录。','result':'补充语录'},
 'intensity':{'tab':'practice','input':'增加追问强度。','result':'追问强度'},
 'experience':{'tab':'experiences','input':'收录一条经验：说明风险时，先说已知和未知，再给核查人、反馈时间和需要的决定。','result':'收录经验'},
}

def free_fixture(source):
 data=json.loads(source);raw=data['input']
 if '新增一个对象' in raw:
  ops=[{'type':'create_object','fields':{'name':'王工','role':'测试负责人','goals':'核实验证记录，推动异常闭环。','style':'说话直接，围绕测试事实与闭环安排交流。','personality':'用户描述：重视验证记录和异常闭环，需结合更多互动核对。'}}]
 elif '更关注验证边界' in raw:
  ops=[{'type':'update_object','objectId':'builtin-project','fields':{'personality':'更关注验证边界（用户观察，待更多场景验证）。'}},{'type':'add_quotes','objectId':'builtin-project','quotes':['条件没验证，就先别承诺交付。']}]
 elif '增加追问强度' in raw:ops=[{'type':'intensity','value':'increase'}]
 elif '收录一条经验' in raw:
  ops=[{'type':'add_experience','title':'先分清已知与未知','category':'项目汇报','content':'说明风险时，先说已知和未知，再给核查人、反馈时间和需要的决定。'}]
 else:raise AssertionError('Unexpected authoring request')
 return {'clarification':'','operations':ops}
