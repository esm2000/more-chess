import React, { useState } from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { BASE_API_URL, useIsMobile } from '../utility';


const BugReportForm = ({ onClose }) => {
    const gameState = GameStateContextData()
    const isMobile = useIsMobile()
    const [description, setDescription] = useState('')
    const [submitted, setSubmitted] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [error, setError] = useState(null)

    const handleSubmit = () => {
        const gameId = sessionStorage.getItem("gameStateId") ?? ""
        const region = Intl.DateTimeFormat().resolvedOptions().timeZone || ""

        setSubmitting(true)
        setError(null)

        fetch(`${BASE_API_URL}/api/bug-report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameId,
                turn: gameState.turnCount,
                description: description,
                region: region
            })
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to submit bug report')
            setSubmitted(true)
            setTimeout(() => onClose(), 1500)
        })
        .catch(err => {
            console.log(err)
            setError('Submission failed. Please try again.')
            setSubmitting(false)
        })
    }

    return (
        <div
            className="pixel-panel"
            style={{
                width: `${isMobile ? 65.0 : 32.5}vw`,
                marginTop: `${isMobile ? 3 : 1.5}vw`,
                borderWidth: `${isMobile ? 2.5 : 1.25}vw`,
                borderTopWidth: `${isMobile ? 0.8 : 0.4}vw`,
                boxSizing: 'border-box',
            }}
        >
            <div style={{
                backgroundColor: 'rgb(71, 33, 1)',
                padding: `${isMobile ? 1 : 0.5}vw 0`,
                textAlign: 'center'
            }}>
                <p style={{
                    fontFamily: 'Basic',
                    fontSize: `${isMobile ? 3 : 1.5}vw`,
                    margin: 0
                }}>~ Bug Report ~</p>
            </div>
            {submitted ? (
                <div style={{
                    padding: `${isMobile ? 3 : 1.5}vw`,
                    textAlign: 'center',
                    fontSize: `${isMobile ? 2.5 : 1.25}vw`,
                    color: 'rgb(80, 220, 80)'
                }}>
                    Sent!
                </div>
            ) : (
                <>
                    <div style={{
                        padding: `${isMobile ? 2 : 1}vw`,
                        borderBottom: `${isMobile ? 0.3 : 0.15}vw solid rgb(71, 33, 1)`
                    }}>
                        <textarea
                            className="bug-report-textarea"
                            placeholder="Describe the bug (optional)"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            rows={3}
                            style={{
                                width: '100%',
                                fontSize: `${isMobile ? 2 : 1}vw`,
                                padding: `${isMobile ? 1 : 0.5}vw`,
                                boxSizing: 'border-box',
                                resize: 'vertical'
                            }}
                        />
                    </div>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: `${isMobile ? 1 : 0.5}vw ${isMobile ? 1.5 : 0.75}vw`,
                    }}>
                        {error ?
                            <span style={{ fontSize: `${isMobile ? 1.4 : 0.7}vw`, color: 'rgb(230, 60, 60)' }}>{error}</span> :
                            <span />
                        }
                        <div style={{ display: 'flex', gap: `${isMobile ? 1 : 0.5}vw` }}>
                            <button
                                className="pixel-btn"
                                onClick={onClose}
                                style={{
                                    fontSize: `${isMobile ? 1.5 : 0.75}vw`,
                                    padding: `${isMobile ? 0.5 : 0.25}vw ${isMobile ? 1 : 0.5}vw`,
                                    borderRadius: `${isMobile ? 0.6 : 0.3}vw`
                                }}
                            >Cancel</button>
                            <button
                                className="pixel-btn"
                                onClick={handleSubmit}
                                disabled={submitting}
                                style={{
                                    fontSize: `${isMobile ? 1.5 : 0.75}vw`,
                                    padding: `${isMobile ? 0.5 : 0.25}vw ${isMobile ? 1 : 0.5}vw`,
                                    borderRadius: `${isMobile ? 0.6 : 0.3}vw`,
                                    opacity: submitting ? 0.5 : 1
                                }}
                            >{submitting ? "Sending..." : "Submit"}</button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

export default BugReportForm;
