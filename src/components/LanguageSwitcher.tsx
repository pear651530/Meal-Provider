import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import twemoji from "twemoji";
import "./LanguageSwitcher.css";

const LanguageSwitcher: React.FC = () => {
    const { i18n } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Language names in their native form
    const nativeLanguageNames: Record<string, string> = {
        zh: "繁體中文",
        en: "English",
    };

    const changeLanguage = (language: string) => {
        i18n.changeLanguage(language);
        setIsOpen(false);
    };

    const getFlagEmoji = (countryCode: string): string => {
        // For Taiwan and US flags
        if (countryCode === "zh") return "🇹🇼"; // Taiwan flag
        if (countryCode === "en") return "🇺🇸"; // US flag
        return "";
    };

    useEffect(() => {
        if (containerRef.current) {
            twemoji.parse(containerRef.current, {
                base: "https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/",
            });
        }
    }, [isOpen, i18n.language]);

    return (
        <div ref={containerRef} className="language-switcher">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="language-button"
            >
                <span className="flag-emoji">
                    {getFlagEmoji(i18n.language)}
                </span>
                <span>{nativeLanguageNames[i18n.language]}</span>
                <span className="dropdown-icon">▼</span>
            </button>

            {isOpen && (
                <div
                    className="language-dropdown"
                    data-testid="language-dropdown"
                >
                    <div
                        onClick={() => changeLanguage("zh")}
                        className={`language-option ${
                            i18n.language === "zh" ? "active" : ""
                        }`}
                    >
                        <span className="flag-emoji">{getFlagEmoji("zh")}</span>
                        <span>{nativeLanguageNames["zh"]}</span>
                    </div>
                    <div
                        onClick={() => changeLanguage("en")}
                        className={`language-option ${
                            i18n.language === "en" ? "active" : ""
                        }`}
                    >
                        <span className="flag-emoji">{getFlagEmoji("en")}</span>
                        <span>{nativeLanguageNames["en"]}</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LanguageSwitcher;
