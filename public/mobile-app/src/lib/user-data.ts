type FoyerAdresseData = {
  code_postal_ville: string;
  complement_information?: string | null;
  complement_information_geographique?: string | null;
  destinataire?: string | null;
  lieu_dit?: string | null;
  numero_libelle_voie: string;
  pays: string;
};

type FoyerPersonData = {
  nom_naissance: string;
  nom_usage?: string | null;
  prenoms: string;
  date_naissance: string;
  sexe: string;
};

type FoyerQuotientFamilialData = {
  annee: number;
  annee_calcul: number;
  fournisseur: string;
  mois: number;
  mois_calcul: number;
  valeur: number;
};

export type FoyerData = {
  adresse?: FoyerAdresseData;
  allocataires?: FoyerPersonData[];
  enfants?: FoyerPersonData[];
  quotient_familial?: FoyerQuotientFamilialData;
  timestamp?: string;
};
