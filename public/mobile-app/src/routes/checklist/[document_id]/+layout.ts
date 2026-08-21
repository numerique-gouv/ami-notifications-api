// @ts-expect-error
import type { PageLoad } from './$types';

// @ts-expect-error
export const load: PageLoad = ({ params }) => {
  if (params.document_id !== 'F16225') {
    window.localStorage[`checklists-${params.document_id}`] = JSON.stringify({
      title: 'Je deviens parent',
      lists: [
        {
          title: 'Pendant la grossesse',
          items: [
            {
              text: '**Avant la fin du 3e mois** de grossesse : passer le **1<sup>er</sup> examen prénatal**, qui permet de faire la **déclaration de grossesse**',
            },
            {
              text: 'Mettre à jour votre **carte Vitale**',
            },
            {
              text: 'Signaler la grossesse à votre **complémentaire santé ou mutuelle**',
            },
            {
              text: 'Si vous n’en avez pas, choisir votre **médecin traitant**',
            },
            {
              text: 'Choisir le **lieu** de votre **accouchement** et vous inscrire',
            },
            {
              text: 'Prendre connaissance des dates des **examens prénataux** et de l’**entretien prénatal précoce**',
            },
            {
              text: "Connaître la **prise en charge** par l'Assurance maladie des **examens médicaux** et des **frais d’accouchement**",
            },
            {
              text: 'Si vous **travaillez**, Informer votre **employeur** et connaître vos droits',
            },
            {
              text: 'Si vous êtes **scolarisée** ou faites des **études universitaires**, connaître vos **droits**',
            },
            {
              text: "Vous renseigner sur les **modes de garde** de l'enfant et sur les **aides financières** existantes",
            },
            {
              text: "Vous renseigner sur vos droits concernant le **congé maternité**, le **congé de naissance**, le **congé de paternité et d'accueil** de l'enfant, le **congé supplémentaire de naissance** et sur les démarches à faire",
            },
            {
              text: '**Avant la fin du 5e mois** de grossesse : si vous le souhaitez, déclarer à l’Assurance Maladie votre **sage-femme référente**',
            },
            {
              text: '**Avant le 7e mois** de grossesse, programmer les **séances de préparation à l’accouchement**',
            },
            {
              text: 'Au **7e mois** de grossesse : vérifier si vous avez perçu la **prime à la naissance**',
            },
            {
              text: 'Au **8e mois** de grossesse : contacter la **sage-femme** qui viendra au domicile **après la sortie de la maternité**',
            },
            {
              text: 'Si vous n’êtes pas mariés, faire la démarche de **reconnaissance** de l’enfant',
              condition: [
                {
                  type: 'estVrai',
                  var: 'T19468',
                },
              ],
            },
            {
              text: 'Vous renseigner sur le **nom de famille** qu’aura l’enfant et choisir son **prénom**',
            },
          ],
        },
        {
          title: 'Après la naissance',
          items: [
            {
              text: '**Dans les 5 jours** qui suivent l’accouchement, faire la **déclaration de naissance** à la mairie',
            },
            {
              text: '**Avant la sortie de la maternité **(ou juste après), renseigner le **1<sup>er</sup> certificat de santé** et recevoir le **carnet de santé**',
            },
            {
              text: '**Déclarer la naissance** à la **Sécurité sociale** et à la **mutuelle**',
            },
            {
              text: "**Rattacher** l'enfant sur les **cartes Vitale des 2 parents**",
            },
            {
              text: "En cas de **dépassements d'honoraires** et/ou de **frais pour confort** personnel à la **maternité**, envoyer les **justificatifs** à votre **complémentaire santé**",
            },
            {
              text: "**Dans les 7 jours** après l'accouchement, recevoir à domicile la **sage-femme**",
            },
            {
              text: '**Déclarer** la naissance à la **Caf**',
              condition: [
                {
                  type: 'estVrai',
                  var: 'T11332',
                },
              ],
            },
            {
              text: 'Prendre connaissance du **suivi médical** de la mère',
            },
            {
              text: "Respecter les dates des **examens médicaux** et des **vaccinations** de l'enfant",
            },
            {
              text: "Connaître les **droits** et vos **obligations** pendant le **congé de maternité** après la naissance, le **congé de naissance**, le **congé de paternité et d'accueil** de l’enfant, le **congé supplémentaire de naissance**",
            },
            {
              text: "Vous renseigner sur le **congé parental**, qui permet de cesser votre travail ou de réduire votre temps de travail pour vous occuper de l'enfant",
            },
            {
              text: 'Connaître vos **droits** quand vous **reprenez le travail**',
            },
            {
              text: "Demander les **prestations familiales**, notamment l'allocation de base de la Paje",
            },
            {
              text: 'Si vous êtes **imposable sur le revenu**, signaler la naissance au **service des impôts** pour la **modification** de votre **taux de prélèvement à la source**',
            },
            {
              text: "Si vous le souhaitez, faire établir la **carte d'identité** et/ou le **passeport** de l'enfant",
            },
            {
              text: 'En cas de **changement de situation** (familiale, professionnelle, déménagement), **informer** l’**Assurance maladie** et la **caisse qui vous verse les prestations familiales**',
            },
            {
              text: "**L’année** où votre enfant atteint l’âge de **3 ans**, **l’inscrire à l'école** en vous y prenant **suffisamment tôt**",
            },
          ],
        },
      ],
    });
  }
  return { document_id: params.document_id };
};
