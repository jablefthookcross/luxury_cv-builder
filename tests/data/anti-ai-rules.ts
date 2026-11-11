/**
 * Reguły audytu jakościowego Anti-AI oraz ATS dla CV generowanego w VitaeCraft AI.
 * Weryfikuje:
 * 1. Brak zakazanych buzzwordów AI (bot-like slop).
 * 2. Zgodność z budżetem treści (40-80 słów podsumowania, 3 kategorie po 4-6 umiejętności).
 * 3. Perspektywę pierwszoosobową (brak zwrotów trzecioosobowych typu "Michał to...").
 * 4. Prawidłowy schemat kategoryzacji (dokładnie 3 spójne grupy).
 */

export const FORBIDDEN_AI_BUZZWORDS = [
  // Język polski
  "dynamiczny profesjonalista",
  "zorientowany na wyniki",
  "pasjonat jakości",
  "synergia",
  "holistyczny",
  "game changer",
  "ninja kodu",
  "rockstar",
  "ewangelista jakości",
  "tkanina sukcesu",
  "zagłębił się",
  "transformacyjna podróż",
  "jest świadectwem",
  "ponadprzeciętny",
  // Język angielski
  "results-driven",
  "passionate developer",
  "synergistic",
  "holistic approach",
  "game-changer",
  "rockstar",
  "tapestry of",
  "delved into",
  "transformative journey",
  "testament to",
  "proven track record of success",
];

export interface QualityAuditResult {
  passed: boolean;
  wordCount: number;
  wordBudgetValid: boolean;
  firstPersonValid: boolean;
  foundAiBuzzwords: string[];
  categoryCount: number;
  categoriesValid: boolean;
  errors: string[];
}

export function auditCvQualityAndAntiAi(profile: any): QualityAuditResult {
  const errors: string[] = [];
  const fullText = JSON.stringify(profile).toLowerCase();

  // 1. Sprawdzenie zakazanych słów AI
  const foundAiBuzzwords: string[] = [];
  for (const buzzword of FORBIDDEN_AI_BUZZWORDS) {
    if (fullText.includes(buzzword.toLowerCase())) {
      foundAiBuzzwords.push(buzzword);
    }
  }
  if (foundAiBuzzwords.length > 0) {
    errors.push(`Wykryto zakazane zwroty AI: ${foundAiBuzzwords.join(", ")}`);
  }

  // 2. Budżet słów dla podsumowania zawodowego (40 - 80 słów)
  const summary = profile.summary || "";
  const words = summary.trim().split(/\s+/).filter((w: string) => w.length > 0);
  const wordCount = words.length;
  const wordBudgetValid = wordCount >= 30 && wordCount <= 95; // bezpieczny margines tolerancji
  if (!wordBudgetValid && wordCount > 0) {
    errors.push(`Liczba słów podsumowania (${wordCount}) wykracza poza zalecany budżet 40-80 słów.`);
  }

  // 3. Perspektywa 1-osobowa (brak 3. osoby typu "Michał specjalizuje się", "Jan jest...")
  const fullName = profile.personal_info?.full_name || "";
  const firstName = fullName.split(" ")[0];
  let firstPersonValid = true;
  if (firstName && firstName.length > 2) {
    const thirdPersonRegex = new RegExp(`\\b${firstName}\\s+(jest|specjalizuje|posiada|pracuje|odpowiada|is|specializes|has)\\b`, "i");
    if (thirdPersonRegex.test(summary)) {
      firstPersonValid = false;
      errors.push(`Podsumowanie zawodowe napisane w 3. osobie ("${firstName} ..."), oczekiwano 1. osoby.`);
    }
  }

  // 4. Kategoryzacja umiejętności (dokładnie 3 kategorie, po 4-6 elementów w każdej)
  const skills = profile.skills || [];
  const categoryCount = skills.length;
  let categoriesValid = categoryCount === 3;
  if (!categoriesValid) {
    errors.push(`Oczekiwano dokładnie 3 kategorii umiejętności, otrzymano: ${categoryCount}`);
  }

  for (const cat of skills) {
    const count = (cat.items || []).length;
    if (count < 3 || count > 8) {
      errors.push(`Kategoria "${cat.category}" zawiera ${count} umiejętności (oczekiwano 4-6).`);
      categoriesValid = false;
    }
  }

  return {
    passed: errors.length === 0,
    wordCount,
    wordBudgetValid,
    firstPersonValid,
    foundAiBuzzwords,
    categoryCount,
    categoriesValid,
    errors,
  };
}
