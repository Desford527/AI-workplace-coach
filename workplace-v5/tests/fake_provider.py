"""Explicit local TEST DOUBLE. Never a production fallback or real model result."""
import http.server
import json
import re
import threading

DIMS=['结论清晰','证据具体','诉求对齐','边界与风险','下一步行动','理解与协作']
class Provider(http.server.BaseHTTPRequestHandler):
    calls=[]
    mode='ok'
    def log_message(self,*args): pass
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        type(self).calls.append({'path':self.path,'body':body})
        mode=type(self).mode
        if mode in ('http','payment'):
            self.send_response(402 if mode=='payment' else 503);self.end_headers();return
        if mode=='delay':
            threading.Event().wait(.4)
        if mode=='unsupported-json' and body.get('response_format'):
            self.send_response(400);self.end_headers();self.wfile.write(b'{"error":"response_format json_object is not supported"}');return
        prompt=body['messages'][0]['content']
        user=body['messages'][-1]['content']
        if '分析完整记录' in prompt:
            user=next(m['content'] for m in body['messages'] if m['role']=='user' and m['content'].startswith('['))
        elif '长期沟通画像' in prompt:
            user=next(m['content'] for m in body['messages'] if m['role']=='user' and m['content'].startswith('{'))
        if mode=='json' or (mode=='flaky-json' and len(type(self).calls)==1): content='not-json'
        elif '连接测试' in prompt: content=json.dumps({'ok':True})
        elif '长期沟通画像' in prompt:
            if mode=='portrait-fail': content='bad portrait'
            else:
                sources=json.loads(user)['sessions'];s=sources[0];m=next(m for m in s['messages'] if m['role']=='user')
                ev={'sessionId':s['id'],'messageId':m['id'],'quote':m['text']}
                item={'title':'初步表达观察（替身）','description':'此为测试替身的协议数据，不代表模型评价。','evidence':[ev]}
                content=json.dumps({'summary':'仅用于自动化验收的画像替身','traits':[item],'strengths':[item],'directions':[{**item,'action':'练习先结论再证据'}]})
        elif '分析完整记录' in prompt:
            if mode=='review-delay':threading.Event().wait(2)
            messages=json.loads(user);users=[m for m in messages if m['role']=='user'];bots=[m for m in messages if m['role']=='assistant']
            def dims(m): return [{'name':n,'score':41+i*7,'basis':'测试替身评分依据','evidence':[{'messageId':m['id'],'quote':m['text']}]} for i,n in enumerate(DIMS)]
            o={'overall':'测试替身复盘，非真实模型验证','sampleLimit':'样本有限，仅用于协议测试','dims':dims(users[0]),
               'timeline':[{'messageId':m['id'],'dims':dims(m),'feedback':'测试替身逐轮反馈','improved':'I will confirm [pending information] by [date].'} for m in users],
               'translations':[{'messageId':m['id'],'surface':'测试表面问题','real':'模拟关切','hidden':'模拟判断依据'} for m in bots],
               'loss':[{'title':'测试问题','desc':'测试依据','action':'测试调整措施'}], 'next':['练习下一步行动'],'language':'中文复盘，英文示范'}
            review_calls=sum('分析完整记录' in r['body']['messages'][0]['content'] for r in type(self).calls)
            if mode=='flaky-schema' and review_calls==1:o['dims'].pop()
            if mode=='bad-score': o['dims'][0]['score']=101
            if mode=='missing-dim': o['dims'].pop()
            if mode=='bad-evidence': o['dims'][0]['evidence'][0]['messageId']='nonexistent'
            if mode=='missing-turn': o['timeline'].pop()
            if mode=='bad-quote': o['dims'][0]['evidence'][0]['quote']='模型杜撰的原话'
            if mode=='bad-round':o['timeline'][0]['dims'][0]['score']=None
            if mode=='next-long':o['next']=['实际模型计划 '+str(i) for i in range(6)]
            if mode=='next-text':o['next']='1. 先说结论\n2. 给出证据'
            if mode=='next-empty':o['next']=[]
            if mode=='long-review':
                o['summary']='结构完整，但关键事实和决策请求仍需具体化。'
                o['overall']='你主动给出推进判断，说明卡点和责任，汇报结构比较完整。主要问题是缺少可核查的事实：测试结果、完成时间和需要协调的事项还未明确，领导难以据此判断风险。建议先用一句话交代当前结论，再补充真实的验证结果、负责人及下次更新时间。没有确认的数据应标注待核实，避免把承诺说满。提出请求时需要说明希望对方决定什么、何时决定，以及暂时无法决定时的备选安排。下一轮请着重练习把事实、判断和请求分开表达，并保留对未知风险的说明。完整总评末尾保留标记。'
                o['loss']=[{'title':'证据缺少可核查的事实','desc':'有结构但没有说明当前结果及验证口径，沟通对象需要追加核查。','action':'提供已有事实、核查人和下一次更新时间；未知内容明确标注待确认。'}, {'title':'请求需要说明具体决策','desc':'请求未能说明要对方确认什么。','action':'明确提出需要对方决定的优先级、截止时间，以及暂不决定时的安排。'}, {'title':'风险与备选安排还可更清楚','desc':'第三项完整观察保留标记。','action':'说明风险边界与备选方案。'}]
                for t in o['timeline']:
                    t['feedback']='本轮表达已经回应了推进方向，但证据和请求仍缺少细节。需要先交代已核实的事实、尚未确认的风险以及希望对方做出的决定。' * 3 + '完整逐轮点评末尾保留标记。'
                    t['improved']='建议先验证已发现的阻塞项，再确认是否具备按计划推进的条件。我会补充当前已完成的核查结果、尚待确认的风险及核查负责人，并在下一次对齐时更新。对于暂时未知的信息，我会明确标注待确认。需要您协助确认当前优先级及可投入的人手；如果暂时无法增加资源，我们可以先收缩范围、保留核心交付，再根据核查结果决定下一步。' * 3 + '完整改进示范末尾保留标记。'
                o['next']=['先给一句明确判断，再补充已核实的事实。','把请求写成对方可以直接回应的具体决定。','约定负责人、下一次更新时间与备选方案。']
            if mode=='optional-missing':
                for k in ('next','language','sampleLimit','overall','translations'):o.pop(k,None)
                o['loss']=[]
            content=json.dumps(o,ensure_ascii=False)
        else:
            context=json.loads(prompt.split('当前冻结资料：')[1].split('\n模拟对象')[0]);en=context['scene']['lang']=='en'
            answer_count=len([m for m in body['messages'] if m['role']=='user'])
            content=json.dumps({'line':f'What evidence supports your plan? Follow-up {answer_count}.' if en else f'请说明方案的证据和下一步安排。追问 {answer_count}。', 'surface':'请说明依据','real':'模拟核查可执行性','hidden':'事实、边界与行动'},ensure_ascii=False)
        if mode=='fenced':content='```json\n'+content+'\n```'
        if mode=='prose':content='以下是结果：\n'+content+'\n已完成。'
        if mode=='thinking':content='<think>这是测试替身思考</think>\n'+content
        if mode=='double-json':content=json.dumps(content)
        if mode=='blocks':content=[{'type':'text','text':{'value':content}}]
        if mode=='multiple-json':content=content+'\n{}'
        message={'content':content}
        if mode=='reasoning-only':message={'content':None,'reasoning_content':'仅测试思考内容'}
        if mode=='empty':message={'content':''}
        raw=json.dumps({'choices':[{'message':message,'finish_reason':'length' if mode=='truncated' else 'stop'}]}).encode()
        self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers()
        try:self.wfile.write(raw)
        except BrokenPipeError:pass

def start():
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Provider)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server

if __name__=='__main__':
    s=start();print('TEST DOUBLE port',s.server_port,flush=True)
    threading.Event().wait()
