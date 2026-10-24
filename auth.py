"""Cliente por sessão. Nenhuma chave administrativa é usada no aplicativo."""
import requests

class AuthError(Exception): pass

def api(url,key,path,body=None,token=None,method='POST'):
    headers={'apikey':key,'Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    r=requests.request(method,url.rstrip('/')+path,headers=headers,json=body,timeout=20)
    if not r.ok: raise AuthError('Operação não concluída. Confira os dados ou solicite um novo link. Se persistir, contate a MultVet.')
    return r.json() if r.content else None

def entrar(url,key,email,password):
    return api(url,key,'/auth/v1/token?grant_type=password',{'email':email.strip(),'password':password})

def sessao_valida(url,key,session):
    # Refresh explícito, sem compartilhar clientes entre usuários.
    import time
    if session.get('expires_at',0)<time.time()+60:
        session=api(url,key,'/auth/v1/token?grant_type=refresh_token',{'refresh_token':session['refresh_token']})
    user=api(url,key,'/auth/v1/user',token=session['access_token'],method='GET')
    if not user.get('email_confirmed_at'): raise AuthError('Confirme seu email antes de acessar.')
    return session,user
