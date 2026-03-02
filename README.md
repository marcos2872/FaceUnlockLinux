# Plano de implementação – Face Unlock em Python (Linux)

## Objetivo do projeto

Criar um aplicativo desktop em Python que:
- Cadastre rostos via webcam.
- Reconheça o rosto em tempo real.
- Exponha uma interface de autenticação (CLI/daemon) para ser usada por módulos PAM, permitindo unlock de tela, login e sudo no Linux.[web:5][web:22]

---

## Fase 1 – MVP de reconhecimento facial em linha de comando

### Objetivo
Ter um script Python capaz de:
- Cadastrar faces (enrolment) por usuário.
- Autenticar um usuário pela webcam retornando OK/FAIL.[web:20][web:24]

### Tasks

1. **Setup de ambiente**
   - Distro alvo principal vai ser o fedora kde.
   - Criar venv Python.
   - Instalar dependências mínimas:
     - `opencv-python` para captura de webcam.[web:17][web:18]
     - `face_recognition` (dlib) ou outra lib de embeddings faciais.[web:24][web:26]
   - Validar: script simples que abre webcam e mostra vídeo.

2. **Modelo de dados de usuário/face**
   - Definir estrutura em disco:
     - Ex.: `/var/lib/faceunlock/<username>/embeddings.npy` ou `.pkl`.
   - Definir formato:
     - Lista de vetores de embedding.
     - Metadados: data de criação, versão do modelo, threshold.

3. **Script de enrolment (cadastro)**
   - CLI ex.: `faceunlock.py enrol --user <username>`.
   - Capturar N frames do rosto (ex.: 20–50).[web:23]
   - Para cada frame:
     - Detectar rosto.
     - Extrair embedding.
   - Agregar embeddings (média ou lista).
   - Salvar em disco na pasta do usuário.

4. **Script de autenticação**
   - CLI ex.: `faceunlock.py auth --user <username>`.
   - Capturar sequência curta de frames (ex.: 5–10).
   - Para cada frame:
     - Detectar rosto.
     - Extrair embedding.
     - Calcular distância para embeddings salvos.
   - Agregar resultado (ex.: média das menores distâncias).
   - Comparar com threshold e:
     - `exit code 0` para sucesso.
     - `exit code 1` para falha.
   - Logar em stdout / arquivo (para debug).

5. **Ajuste de threshold / qualidade**
   - Criar script simples de teste manual:
     - Testar com seu rosto e de outras pessoas.
   - Ajustar threshold para reduzir falsos positivos/negativos.[web:23]

---

## Fase 2 – Serviço/CLI estável para integração com PAM

### Objetivo
Transformar o script em uma interface de autenticação previsível, pensada para ser chamada por PAM.[web:5][web:22]

### Tasks

6. **Empacotar o CLI**
   - Separar em:
     - Módulo de lógica (`core.py` ou similar).
     - Script CLI (`faceunlock` instalado via `setup.py` ou `pyproject.toml`).
   - Garantir:
     - Interface estável: `faceunlock enrol`, `faceunlock auth`.
     - Códigos de saída consistentes.

7. **Adicionar modo “non-interactive”**
   - Para `auth`, permitir:
     - Rodar sem janelas gráficas (apenas terminal).
     - Timeout configurável.
   - Opção para log em arquivo (ex.: `/var/log/faceunlock.log`).

8. **Diretórios e permissões**
   - Definir diretório de dados “de produção”:
     - Ex.: `/etc/faceunlock/` ou `/var/lib/faceunlock/`.[web:5]
   - Ajustar permissões:
     - Somente root e grupo específico.
   - Criar comando de inicialização:
     - Ex.: `faceunlock init` que cria os diretórios, aplica permissões.

9. **Daemon opcional (se necessário)**
   - Se o tempo de inicialização for alto:
     - Criar processo daemon em Python (ex.: com `socket` UNIX).
     - Cliente CLI se comunica via socket.
   - Senão, manter apenas CLI direto para simplificar.

---

## Fase 3 – Integração inicial com PAM (sem GUI ainda)

### Objetivo
Conseguir logar/autorizar via rosto em algum ponto (por exemplo, `sudo` ou i3lock), usando o CLI.[web:5][web:22]

### Tasks

10. **Estudar e testar PAM com exemplo existente**
    - Ler docs/artigos de PAM e olhar projetos prontos:
      - `pam-face`, `face_unlock_linux`, `hi` (dlib + OpenCV).[web:5][web:22][web:27]
    - Entender:
      - Arquivo `/etc/pam.d/*`.
      - Tipo `auth sufficient` vs `required`.
      - Fallback para senha se falhar.

11. **Configuração experimental**
    - Criar um módulo PAM minimalista (pode começar reaproveitando `pam_exec`):
      - Ex.: usar `pam_exec` para chamar seu `faceunlock auth` para testes.[web:3]
      - Assim, você testa seu CLI com PAM sem escrever C ainda.
    - Exemplo de passo:
      - Em `/etc/pam.d/sudo`, adicionar linha de teste com `pam_exec` chamando seu script.
    - Verificar:
      - Se seu script é chamado.
      - Se o código de saída influencia a autenticação.

12. **Definição da interface final PAM ⇄ CLI**
    - Especificar claramente:
      - Parâmetros: `--user`, `--timeout`, `--config`.
      - Código de saída usado por PAM para “autenticado”.
    - Documentar isso como contrato para futura implementação em módulo C/Rust, se quiser.

---

## Fase 4 – GUI desktop em Python (Qt / PySide6)

### Objetivo
Criar o app desktop que o usuário final usa para cadastrar faces, testar e configurar uso no sistema.[web:6][web:15]

### Tasks

13. **Setup da GUI**
    - Escolher PySide6 (Qt for Python).
    - Criar aplicação básica:
      - Janela principal.
      - Menu/tabs: “Faces”, “Teste”, “Configuração”.
    - Integrar com o core:
      - Importar seus módulos Python de face recognition.

14. **Tela de gerenciamento de faces**
    - Listar usuários/faces cadastrados:
      - Puxar dados de `/var/lib/faceunlock` (ou diretório escolhido).
    - Botões:
      - “Cadastrar nova face”.
      - “Remover face”.
      - “Re-treinar”.

15. **Tela de enrolment com webcam**
    - Usar OpenCV para captura e converter frames para QImage/Qt.
    - UI:
      - Preview da webcam.
      - Retângulo em volta do rosto.
      - Barra de progresso “Coletando imagens”.
    - Reutilizar a lógica do script `enrol`:
      - Mas chamando funções Python internas, não o CLI.

16. **Tela de teste de autenticação**
    - Botão “Testar desbloqueio”.
    - Exibe webcam, tenta autenticar o usuário selecionado.
    - Mostra:
      - Resultado (sucesso/falha).
      - Score (distância/semelhança).

17. **Tela de configuração do sistema**
    - Opções:
      - Selecionar quais serviços usarão face:
        - Login (documentar manualmente no começo).
        - Lockscreen (ex.: i3lock).
        - `sudo`.
      - Threshold de decisão.
    - Botão “Aplicar configuração”:
      - Gera sugestões de trechos PAM.
      - Opcional: roda scripts que editam `/etc/pam.d/*` (com cuidado, exigindo root e backup).

---

## Fase 5 – Refinos de segurança e UX

### Objetivo
Tornar o sistema minimamente seguro e usável em contexto real.

### Tasks

18. **Melhorias de segurança básica**
    - Guardar embeddings e configs em diretórios com permissões restritas.
    - Adicionar opção de 2FA:
      - Face + senha curta (PIN).
    - Documentar claramente limitações:
      - Possível spoof com foto/vídeo (sem liveness detection).[web:23]

19. **Feedback visual tipo “Face ID”**
    - Animações simples:
      - Círculo ao redor do rosto mudando de cor.
      - Mensagens “Aproxime-se”, “Muito escuro”, “Rosto não encontrado”.
    - Mostrar status em tempo real (ex.: “Scaneando…”).

20. **Logs e diagnósticos**
    - Centralizar logs (app + CLI) em um lugar padrão.
    - Tela na GUI para visualizar últimos logs.
    - Botão “Gerar pacote de diagnóstico” (zip com config + logs).

---

## Fase 6 – Empacotamento e distribuição

### Objetivo
Facilitar instalação em outras máquinas Linux.

### Tasks

21. **Empacotamento Python**
    - Criar `pyproject.toml` ou `setup.py`.
    - Publicar em repositório Git (GitHub/GitLab).
    - Gerar pacote instalável (wheel).

22. **Pacotes para distro**
    - Esboçar .deb / .rpm / AUR (mesmo que inicialmente manual).
    - Scripts pós-instalação:
      - Criar diretórios.
      - Ajustar permissões.
      - Instalar entrada de menu para GUI.

23. **Documentação**
    - `README.md` com:
      - Requisitos.
      - Como instalar.
      - Como usar CLI.
      - Como integrar com PAM (passo a passo).
    - `SECURITY.md` com:
      - Avisos de segurança.
      - Recomendações de uso.

---

## Prioridades (o que é mais crítico primeiro)

1. Reconhecimento facial funcionando bem em CLI (Fase 1).
2. CLI estável e pensada para ser chamada por PAM (Fase 2).
3. Integração mínima com PAM usando `pam_exec` (Fase 3).
4. GUI para cadastro de face e teste (Fase 4, partes 13–16).
5. Configuração amigável + segurança básica (Fases 4–5).
6. Empacotamento e doc (Fase 6).
