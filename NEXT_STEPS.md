# Próximos Passos – Configuração de Sistema e Segurança

Este guia contém as etapas manuais para integrar o Face Unlock em outros serviços do Fedora KDE e as recomendações de segurança.

---

## 1. Ativar Face Unlock na Tela de Bloqueio (KDE)

Para que o reconhecimento facial funcione quando você bloqueia a tela (ex: `Win + L`):

1.  Edite o arquivo de configuração do PAM para o KDE:
    ```bash
    sudo nano /etc/pam.d/kde
    ```
2.  Adicione a seguinte linha no topo do arquivo (logo após `#%PAM-1.0`):
    ```pam
    auth sufficient pam_exec.so stdout /home/marcos/Projects/FaceUnlock/venv/bin/python /home/marcos/Projects/FaceUnlock/faceunlock.py auth --user marcos --no-gui
    ```

---

## 2. Ativar Face Unlock no Login (SDDM)

Para entrar no sistema usando o rosto ao ligar o computador:

1.  Edite o arquivo de configuração do gerenciador de login:
    ```bash
    sudo nano /etc/pam.d/sddm
    ```
2.  Adicione a mesma linha no topo:
    ```pam
    auth sufficient pam_exec.so stdout /home/marcos/Projects/FaceUnlock/venv/bin/python /home/marcos/Projects/FaceUnlock/faceunlock.py auth --user marcos --no-gui
    ```

---

## ⚠️ IMPORTANTE: Segurança e Liveness Detection

Atualmente, o sistema utiliza apenas a comparação de embeddings faciais. Isso significa que ele é vulnerável a **ataques de spoofing** (apresentar uma foto impressa ou um vídeo em um celular para a câmera).

### Limitações Atuais:
- **Sem Detecção de Vivacidade:** O sistema não verifica se o rosto é real ou uma representação estática.
- **Ambiente de Luz:** O desempenho pode variar drasticamente em locais muito escuros ou com luz de fundo forte.

### Implementações Futuras (Fase 5):
- **Blink Detection:** Exigir que o usuário pisque os olhos durante a autenticação.
- **Head Movement:** Pedir que o usuário mova a cabeça em uma direção específica.
- **Depth Analysis:** (Se disponível no hardware) Uso de câmeras infravermelho/profundidade.

---

## Dicas de Uso
- Sempre mantenha uma senha forte como fallback. 
- O comando `sudo -k` limpa o cache do sudo, permitindo testar o reconhecimento facial imediatamente.
