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
        prompt=body['messages'][0]['content']
        user=body['messages'][-1]['content']
        if mode=='json': content='not-json'
        elif '连接测试' in prompt: content=json.dumps({'ok':True})
        elif '长期沟通画像' in prompt:
            if mode=='portrait-fail': content='bad portrait'
            else:
                sources=json.loads(user)['sessions'];s=sources[0];m=next(m for m in s['messages'] if m['role']=='user')
                ev={'sessionId':s['id'],'messageId':m['id'],'quote':m['text']}
                item={'title':'初步表达观察（替身）','description':'此为测试替身的协议数据，不代表模型评价。','evidence':[ev]}
                content=json.dumps({'summary':'仅用于自动化验收的画像替身','traits':[item],'strengths':[item],'directions':[{**item,'action':'练习先结论再证据'}]})
        elif '分析完整记录' in prompt:
            messages=json.loads(user);users=[m for m in messages if m['role']=='user'];bots=[m for m in messages if m['role']=='assistant']
            def dims(m): return [{'name':n,'score':41+i*7,'basis':'测试替身评分依据','evidence':[{'messageId':m['id'],'quote':m['text']}]} for i,n in enumerate(DIMS)]
            o={'overall':'测试替身复盘，非真实模型验证','sampleLimit':'样本有限，仅用于协议测试','dims':dims(users[0]),
               'timeline':[{'messageId':m['id'],'dims':dims(m),'feedback':'测试替身逐轮反馈','improved':'I will confirm [pending information] by [date].'} for m in users],
               'translations':[{'messageId':m['id'],'surface':'测试表面问题','real':'模拟关切','hidden':'模拟判断依据'} for m in bots],
               'loss':[{'title':'测试问题','desc':'测试依据','action':'测试调整措施'}], 'next':['练习下一步行动'],'language':'中文复盘，英文示范'}
            if mode=='bad-score': o['dims'][0]['score']=101
            if mode=='missing-dim': o['dims'].pop()
            if mode=='bad-evidence': o['dims'][0]['evidence'][0]['messageId']='nonexistent'
            if mode=='missing-turn': o['timeline'].pop()
            if mode=='bad-quote': o['dims'][0]['evidence'][0]['quote']='模型杜撰的原话'
            if mode=='bad-round':o['timeline'][0]['dims'][0]['score']=None
            content=json.dumps(o,ensure_ascii=False)
        else:
            context=json.loads(prompt.split('当前冻结资料：')[1].split('\n模拟对象')[0]);en=context['scene']['lang']=='en'
            answer_count=len([m for m in body['messages'] if m['role']=='user'])
            content=json.dumps({'line':f'What evidence supports your plan? Follow-up {answer_count}.' if en else f'请说明方案的证据和下一步安排。追问 {answer_count}。', 'surface':'请说明依据','real':'模拟核查可执行性','hidden':'事实、边界与行动'},ensure_ascii=False)
        raw=json.dumps({'choices':[{'message':{'content':content}}]}).encode()
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
