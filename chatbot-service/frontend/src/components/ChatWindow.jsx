import React, { useState } from 'react';
import { sendMessageToChatbot } from '../api/chatbotAPI';

// Hardcoded rules from backend/src/data/rules.json
const RULES = [
    {
        pattern: "Qu'est-ce que l'EST Salé ?",
        answer: "L'École Supérieure de Technologie de Salé (EST-Salé) est un établissement public d'enseignement supérieur professionnel rattaché à l'Université Mohammed V de Rabat, inauguré en 1993-1994. Elle forme en deux ans des techniciens supérieurs via le DUT, avec une offre de Licence professionnelle depuis 2014–2015."
    },
    {
        pattern: "Quelles sont les filières disponibles ?",
        answer: "Filières DUT (Bac+2) : Techniques de Management, Marketing & Techniques de Commercialisation, Environnement et Techniques de l'Eau, Génie Civil, Construction & Énergétique du Bâtiment, Génie Bio‑Industriel, Administration Réseau Informatiques, Génie Logiciel, Génie Électrique & Informatique Industrielle, Génie Industriel & Maintenance. Licences Professionnelles : Efficience Énergétique & Acoustique du Bâtiment, Génie Civil, Logistique de Distribution, Ingénierie des Applications Mobiles, Instrumentation & Maintenance Biomédicale, Maintenance des Équipements Scientifiques, Diagnostic & Maintenance des Systèmes Électroniques Embarqués (automobile)."
    },
    {
        pattern: "Quels sont les chiffres clés ?",
        answer: "L'EST Salé compte environ 84 enseignants permanents et 96 personnels administratifs, 1300 étudiants en DUT et 120 en Licence pro, 10 filières DUT et 6 filières LP en initial, avec un taux de diplômation proche de 100%. L'infrastructure comprend 5 hectares, 2 amphithéâtres (250 places), salles, laboratoires, bibliothèques, 900 postes informatiques et un complexe omnisport."
    },
    {
        pattern: "Comment s'inscrire ?",
        answer: "Pour le DUT : inscription en ligne via le portail préinscription.um5.ac.ma, sur sélection (75% Bac national + 25% Bac régional). Pour la Licence pro : préinscriptions en ligne (dates variables), sélection via dossier et concours écrit/entretien."
    },
    {
        pattern: "Contact EST Salé",
        answer: "Téléphone : 05 37 88 15 61 / 62 / 63, Email : ests@um5.ac.ma, Adresse : Avenue Prince Héritier, B.P. 227, Salé 11000, Maroc, Site officiel : http://est.um5.ac.ma"
    }
];

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
    const [showSuggestions, setShowSuggestions] = useState(true);

    const handleSend = async () => {
        if (!input.trim()) return;
        setMessages([...messages, { from: 'user', text: input }]);
        setLoading(true);
        setError('');
        setShowSuggestions(false);
        try {
            const res = await sendMessageToChatbot(input, token);
            setMessages((msgs) => [...msgs, { from: 'bot', text: res.response }]);
        } catch (e) {
            setError("Erreur lors de la communication avec le chatbot.");
        }
        setInput('');
        setLoading(false);
    };

    // Handle clicking a suggestion
    const handleSuggestion = (pattern, answer) => {
        setMessages([...messages, { from: 'user', text: pattern }, { from: 'bot', text: answer }]);
        setShowSuggestions(false);
        setConversationStarted(true);
    };

    const ChatButton = (
        <button
            onClick={() => setOpen(true)}
            style={{
                position: 'fixed',
                right: 20,
                bottom: 20,
                width: 56,
                height: 56,
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
            <svg width="28" height="28" fill="#fff" viewBox="0 0 24 24">
                <path d="M2 21l1.65-4.95A8.963 8.963 0 0 1 2 12C2 6.48 7.03 2 13 2s11 4.48 11 10-5.03 10-11 10c-1.61 0-3.16-.25-4.6-.7L2 21z" />
            </svg>
        </button>
    );

    const ChatPanel = (
        <div style={{
            position: 'fixed',
            right: 0,
            bottom: 0,
            height: '100vh',
            width: 400,
            maxWidth: '100vw',
            background: '#fff',
            boxShadow: '2px 0 12px #0002',
            zIndex: 1100,
            display: 'flex',
            flexDirection: 'column',
            borderTopRightRadius: 16,
            borderRight: '1px solid #eee',
            borderTop: '1px solid #eee',
        }}>
            <div style={{ background: '#ff8000', color: '#fff', padding: 24, fontSize: 24, fontWeight: 700, borderTopRightRadius: 16 }}>
                Bienvenue
                <div style={{ fontSize: 16, fontWeight: 400, marginTop: 4 }}>Nous sommes là pour vous aider</div>
                <button
                    onClick={() => setOpen(false)}
                    style={{ position: 'absolute', right: 16, top: 16, background: 'none', border: 'none', color: '#fff', fontSize: 24, cursor: 'pointer' }}
                    aria-label="Fermer le chatbot"
                >×</button>
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: 24, background: '#faf9f7' }}>
                {/* Conversation launcher and suggestions */}
                {!conversationStarted && (
                    <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', marginBottom: 24, padding: 20 }}>
                        <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 12 }}>Lancer une conversation</div>
                        <button
                            onClick={() => { setConversationStarted(true); setShowSuggestions(true); }}
                            style={{ background: '#ff8000', color: '#fff', border: 'none', borderRadius: 6, padding: '12px 24px', fontSize: 18, fontWeight: 700, boxShadow: '0 2px 8px #0002', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                        >
                            <svg width="24" height="24" fill="#fff" style={{ marginRight: 8 }} viewBox="0 0 24 24"><path d="M2 21l21-9-21-9v7l15 2-15 2z" /></svg>
                            Envoyez-nous un message
                        </button>
                        {/* Suggestions */}
                        {showSuggestions && (
                            <div style={{ marginTop: 18, display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                                {RULES.map((rule, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleSuggestion(rule.pattern, rule.answer)}
                                        style={{ background: '#fff', color: '#ff8000', border: '2px solid #ff8000', borderRadius: 20, padding: '8px 16px', fontWeight: 600, cursor: 'pointer', marginBottom: 6 }}
                                    >
                                        {rule.pattern}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                )}
                {/* Chat conversation */}
                {conversationStarted && (
                    <div style={{ marginBottom: 24 }}>
                        <div style={{ height: 220, overflowY: 'auto', background: '#fff', borderRadius: 8, padding: 16, boxShadow: '0 2px 8px #0001', marginBottom: 12 }}>
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
                        {/* Suggestions after conversation started */}
                        {showSuggestions && (
                            <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                                {RULES.map((rule, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleSuggestion(rule.pattern, rule.answer)}
                                        style={{ background: '#fff', color: '#ff8000', border: '2px solid #ff8000', borderRadius: 20, padding: '8px 16px', fontWeight: 600, cursor: 'pointer', marginBottom: 6 }}
                                    >
                                        {rule.pattern}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                )}
                {/* Search card */}
                <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', marginBottom: 24, padding: 20 }}>
                    <div style={{ fontSize: 20, fontWeight: 600, marginBottom: 10 }}>Que recherchez-vous ?</div>
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Rechercher un sujet..."
                        style={{ width: '100%', border: '1px solid #ccc', borderRadius: 16, padding: '8px 14px', fontSize: 16, marginBottom: 8 }}
                    />
                    {/* Show suggestions based on search */}
                    {search && (
                        <div style={{ marginTop: 8 }}>
                            {RULES.filter(rule => rule.pattern.toLowerCase().includes(search.toLowerCase())).map((rule, idx) => (
                                <div key={idx} style={{ padding: '6px 0', color: '#ff8000', fontWeight: 500 }}>
                                    {rule.pattern}
                                </div>
                            ))}
                            {RULES.filter(rule => rule.pattern.toLowerCase().includes(search.toLowerCase())).length === 0 && (
                                <div style={{ color: '#888' }}>Aucun résultat trouvé.</div>
                            )}
                        </div>
                    )}
                </div>
                {/* Co-navigation card */}
                <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001', padding: 20 }}>
                    <div style={{ fontSize: 20, fontWeight: 600, marginBottom: 10 }}>Parcourez cette page avec nous</div>
                    <button style={{ background: '#ff8000', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 20px', fontSize: 16, fontWeight: 700, display: 'flex', alignItems: 'center', boxShadow: '0 2px 8px #0002', cursor: 'pointer' }}>
                        <svg width="20" height="20" fill="#fff" style={{ marginRight: 8 }} viewBox="0 0 24 24"><path d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2zm-2 0H5V5h14v14zm-7-3l-5-5h3V7h4v4h3l-5 5z" /></svg>
                        Rejoindre la co-navigation
                    </button>
                    <div style={{ color: '#888', fontSize: 14, marginTop: 8 }}>
                        Cette fonctionnalité vous permet de parcourir la page avec un conseiller en temps réel (bientôt disponible).
                    </div>
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