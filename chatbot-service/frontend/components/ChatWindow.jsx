import React, { useState } from 'react';
import { sendMessageToChatbot } from '../api/chatbotAPI';

const ChatWindow = ({ token }) => {
    const [open, setOpen] = useState(false);
    const [conversationStarted, setConversationStarted] = useState(false);
    const [messages, setMessages] = useState([
        { from: 'bot', text: 'Bienvenue ! Nous sommes là pour vous aider.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [search, setSearch] = useState('');

    const handleSend = async () => {
        if (!input.trim()) return;
        setMessages([...messages, { from: 'user', text: input }]);
        setLoading(true);
        setError('');
        try {
            const res = await sendMessageToChatbot(input);
            setMessages((msgs) => [...msgs, { from: 'bot', text: res.response }]);
        } catch (e) {
            setError("Erreur lors de la communication avec le chatbot.");
        }
        setInput('');
        setLoading(false);
    };

    const ChatButton = (
        <button
            onClick={() => setOpen(true)}
            style={{
                position: 'fixed',
                left: 20,
                top: 20,
                width: 48,
                height: 48,
                borderRadius: '50%',
                background: '#ff8000',
                border: 'none',
                boxShadow: '0 2px 8px #0002',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                cursor: 'pointer',
            }}
            aria-label="Ouvrir le chatbot"
        >
            <svg width="24" height="24" fill="#fff" viewBox="0 0 24 24">
                <path d="M2 21l1.65-4.95A8.963 8.963 0 0 1 2 12C2 6.48 7.03 2 13 2s11 4.48 11 10-5.03 10-11 10c-1.61 0-3.16-.25-4.6-.7L2 21z" />
            </svg>
        </button>
    );

    const ChatPanel = (
        <div style={{
            position: 'fixed',
            left: 0,
            top: 0,
            height: '100vh',
            width: 400,
            maxWidth: '100vw',
            background: '#fff',
            boxShadow: '2px 0 12px #0002',
            zIndex: 1100,
            display: 'flex',
            flexDirection: 'column',
            transition: 'transform 0.3s',
            borderRight: '1px solid #eee',
        }}>
            <div style={{ background: '#ff8000', color: '#fff', padding: 24, fontSize: 24, fontWeight: 700 }}>
                Bienvenue
                <div style={{ fontSize: 16, fontWeight: 400, marginTop: 4 }}>Nous sommes là pour vous aider</div>
                <button
                    onClick={() => setOpen(false)}
                    style={{ position: 'absolute', right: 16, top: 16, background: 'none', border: 'none', color: '#fff', fontSize: 24, cursor: 'pointer' }}
                    aria-label="Fermer le chatbot"
                >×</button>
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: 24, background: '#faf9f7' }}>
                {!conversationStarted && (
                    <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', marginBottom: 24, padding: 20 }}>
                        <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 12 }}>Lancer une conversation</div>
                        <button
                            onClick={() => setConversationStarted(true)}
                            style={{ background: '#ff8000', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 24px', fontSize: 18, fontWeight: 700, boxShadow: '0 2px 8px #0002', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                        >
                            <svg width="24" height="24" fill="#fff" style={{ marginRight: 8 }} viewBox="0 0 24 24"><path d="M2 21l21-9-21-9v7l15 2-15 2z" /></svg>
                            Envoyez-nous un message
                        </button>
                    </div>
                )}
                {conversationStarted && (
                    <div style={{ marginBottom: 24 }}>
                        <div style={{ height: 260, overflowY: 'auto', background: '#fff', borderRadius: 8, padding: 16, boxShadow: '0 2px 8px #0001', marginBottom: 12 }}>
                            {messages.map((msg, idx) => (
                                <div key={idx} style={{ textAlign: msg.from === 'bot' ? 'left' : 'right', margin: '8px 0' }}>
                                    <span style={{ background: msg.from === 'bot' ? '#eee' : '#ff8000', color: msg.from === 'bot' ? '#333' : '#fff', padding: '6px 12px', borderRadius: 16, display: 'inline-block' }}>{msg.text}</span>
                                </div>
                            ))}
                            {loading && <div style={{ color: '#888' }}>Le bot réfléchit...</div>}
                            {error && <div style={{ color: 'red' }}>{error}</div>}
                        </div>
                        <div style={{ display: 'flex', borderTop: '1px solid #eee', padding: 8, background: '#fff', borderRadius: 8 }}>
                            <input
                                type="text"
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleSend()}
                                placeholder="Écrivez votre message..."
                                style={{ flex: 1, border: '1px solid #ccc', borderRadius: 16, padding: '6px 12px' }}
                                disabled={loading}
                            />
                            <button onClick={handleSend} disabled={loading || !input.trim()} style={{ marginLeft: 8, background: '#ff8000', color: '#fff', border: 'none', borderRadius: 16, padding: '6px 16px', cursor: 'pointer' }}>
                                Envoyer
                            </button>
                        </div>
                    </div>
                )}
                <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', marginBottom: 24, padding: 20 }}>
                    <div style={{ fontSize: 20, fontWeight: 600, marginBottom: 10 }}>Que recherchez-vous ?</div>
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Rechercher un sujet..."
                        style={{ width: '100%', border: '1px solid #ccc', borderRadius: 16, padding: '8px 14px', fontSize: 16 }}
                    />
                </div>
                <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', padding: 20 }}>
                    <div style={{ fontSize: 20, fontWeight: 600, marginBottom: 10 }}>Parcourez cette page avec nous</div>
                    <button style={{ background: '#ff8000', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 20px', fontSize: 16, fontWeight: 700, display: 'flex', alignItems: 'center', boxShadow: '0 2px 8px #0002', cursor: 'pointer' }}>
                        <svg width="20" height="20" fill="#fff" style={{ marginRight: 8 }} viewBox="0 0 24 24"><path d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2zm-2 0H5V5h14v14zm-7-3l-5-5h3V7h4v4h3l-5 5z" /></svg>
                        Rejoindre la co-navigation
                    </button>
                </div>
            </div>
        </div>
    );

    return (
        <>
            {!open && ChatButton}
            {open && ChatPanel}
        </>
    );
};

export default ChatWindow;