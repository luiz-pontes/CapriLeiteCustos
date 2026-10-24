import streamlit as st
from urllib.parse import quote
from auth import api, entrar, sessao_valida, AuthError

def proteger():
    try:
        URL=st.secrets['SUPABASE_URL']; KEY=st.secrets['SUPABASE_PUBLISHABLE_KEY']; APP=st.secrets['APP_URL'].rstrip('/')
    except Exception:
        st.info('Configure as credenciais públicas do projeto MultVet e o endereço do aplicativo em Settings → Secrets.');st.stop()
    
    # Os templates de email usam token_hash na query; fragmentos #access_token não são aceitos.
    if st.query_params.get('token_hash'):
        typ=st.query_params.get('type','')
        if typ not in ['invite','recovery','signup','email']:
            st.error('Tipo de link inválido.');st.stop()
        st.info('Confirme abaixo para continuar com o link recebido por email.')
        if st.button('Confirmar link e continuar'):
            try:
                session=api(URL,KEY,'/auth/v1/verify',{'token_hash':st.query_params['token_hash'],'type':typ})
                st.session_state['auth']=session
                st.session_state['definir_senha']=typ in ['invite','recovery']
                st.query_params.clear();st.rerun()
            except (AuthError, Exception): st.error('Link inválido ou vencido. Solicite um novo email.')
        st.stop()
    
    if 'auth' not in st.session_state:
        tab1,tab2,tab3=st.tabs(['Entrar','Criar conta','Esqueci minha senha'])
        with tab1:
            with st.form('entrar'):
                email=st.text_input('Email usado na compra');pw=st.text_input('Senha',type='password')
                go=st.form_submit_button('Entrar')
            if go:
                try: st.session_state['auth']=entrar(URL,KEY,email,pw);st.rerun()
                except Exception: st.error('Não foi possível entrar. Confira email e senha e confirme seu email.')
        with tab2:
            st.write('Crie sua conta com o mesmo email da compra. Criar uma conta não libera o produto automaticamente.')
            with st.form('cadastro'):
                em=st.text_input('Email da compra');p1=st.text_input('Senha (mínimo 12 caracteres)',type='password');p2=st.text_input('Repita a senha',type='password')
                go2=st.form_submit_button('Criar conta')
            if go2:
                if len(p1)<12 or p1!=p2: st.error('Use ao menos 12 caracteres e repita a mesma senha.')
                else:
                    try:
                        api(URL,KEY,'/auth/v1/signup?redirect_to='+quote(APP,safe=''),{'email':em.strip(),'password':p1})
                        st.success('Se o cadastro puder ser realizado, você receberá instruções por email. Confira também o spam.')
                    except Exception: st.error('Não foi possível concluir. Se já recebeu um convite, use o link do convite ou a recuperação de senha.')
        with tab3:
            with st.form('recuperar'):
                emr=st.text_input('Seu email');gor=st.form_submit_button('Enviar recuperação')
            if gor:
                try:
                    api(URL,KEY,'/auth/v1/recover?redirect_to='+quote(APP,safe=''),{'email':emr.strip()})
                    st.success('Se houver uma conta elegível, enviaremos instruções. Confira seu email e o spam.')
                except Exception: st.error('Não foi possível enviar agora. Tente novamente mais tarde.')
        st.stop()
    
    try:
        session,user=sessao_valida(URL,KEY,st.session_state['auth']);st.session_state['auth']=session
    except Exception:
        st.session_state.pop('auth',None);st.error('Sessão expirada ou indisponível. Entre novamente.');st.stop()
    with st.sidebar:
        st.write(user.get('email',''))
        if st.button('Sair'):
            try: api(URL,KEY,'/auth/v1/logout',token=session['access_token'])
            except Exception: pass
            st.session_state.clear();st.rerun()
    
    if st.session_state.get('definir_senha'):
        with st.form('nova_senha'):
            st.subheader('Defina sua senha')
            p1=st.text_input('Nova senha (mínimo 12 caracteres)',type='password');p2=st.text_input('Repita a nova senha',type='password');go=st.form_submit_button('Salvar senha')
        if go:
            if len(p1)<12 or p1!=p2: st.error('Confira o tamanho e a repetição da senha.')
            else:
                try:
                    api(URL,KEY,'/auth/v1/user',{'password':p1},session['access_token'],method='PUT')
                    st.session_state['definir_senha']=False;st.rerun()
                except Exception: st.error('Não foi possível atualizar. Solicite outro link de recuperação.')
        st.stop()
    
    # Autorização no servidor em todo rerun; falha de conexão bloqueia os cálculos.
    try: access=api(URL,KEY,'/rest/v1/rpc/multvet_acesso_lucroleite',{},session['access_token'])
    except Exception:
        st.error('Não foi possível verificar seu acesso. Tente novamente; se persistir, contate a MultVet.');st.stop()
    if not access:
        st.info('Não encontramos acesso ativo a este produto. Confira o email usado na compra. O acesso depende da aprovação do pagamento e do prazo contratado.');st.stop()
    st.sidebar.caption('Acesso válido até '+access[0]['fim_acesso'][:10])
