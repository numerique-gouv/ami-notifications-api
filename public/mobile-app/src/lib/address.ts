export type AddressOrigin = 'user' | 'api-particulier' | 'cleared'

export class Address {
  constructor(
    private _city: string = '',
    private _context: string = '',
    private _idBAN: string = '',
    private _label: string = '',
    private _name: string = '',
    private _postcode: string = ''
  ) {}

  static fromJSON(json: any): Address {
    return new Address(
      json._city,
      json._context,
      json._idBAN,
      json._label,
      json._name,
      json._postcode
    )
  }

  get city(): string {
    return this._city
  }

  get context(): string {
    return this._context
  }

  get idBAN(): string {
    return this._idBAN
  }

  get label(): string {
    return this._label
  }

  get name(): string {
    return this._name
  }

  get postcode(): string {
    return this._postcode
  }

  get departement(): string {
    if (this._postcode.length < 2) {
      return ''
    }
    return this._postcode.substring(0, 2)
  }

  get zone(): string {
    const academie = academies.find((a) => {
      return a.departements.includes(this.departement)
    })
    return academie ? academie.zone : ''
  }
}

const academies = [
  { academie: 'Aix-Marseille', departements: ['04', '05', '13', '84'], zone: 'B' },
  { academie: 'Amiens', departements: ['02', '60', '80'], zone: 'B' },
  { academie: 'Besançon', departements: ['25', '39', '70', '90'], zone: 'A' },
  { academie: 'Bordeaux', departements: ['24', '33', '40', '47', '64'], zone: 'A' },
  { academie: 'Clermont-Ferrand', departements: ['03', '15', '43', '63'], zone: 'A' },
  { academie: 'Créteil', departements: ['77', '93', '94'], zone: 'C' },
  { academie: 'Dijon', departements: ['21', '58', '71', '89'], zone: 'A' },
  { academie: 'Grenoble', departements: ['07', '26', '38', '73', '74'], zone: 'A' },
  { academie: 'Lille', departements: ['59', '62'], zone: 'B' },
  { academie: 'Limoges', departements: ['19', '23', '87'], zone: 'A' },
  { academie: 'Lyon', departements: ['01', '42', '69'], zone: 'A' },
  { academie: 'Montpellier', departements: ['11', '30', '34', '48', '66'], zone: 'C' },
  { academie: 'Nancy-Metz', departements: ['54', '55', '57', '88'], zone: 'B' },
  { academie: 'Nantes', departements: ['44', '49', '53', '72', '85'], zone: 'B' },
  { academie: 'Nice', departements: ['06', '83'], zone: 'B' },
  { academie: 'Normandie', departements: ['14', '27', '50', '61', '76'], zone: 'B' },
  {
    academie: 'Orléans-Tours',
    departements: ['18', '28', '36', '37', '41', '45'],
    zone: 'B',
  },
  { academie: 'Paris', departements: ['75'], zone: 'C' },
  { academie: 'Poitiers', departements: ['16', '17', '79', '86'], zone: 'A' },
  { academie: 'Reims', departements: ['08', '10', '51', '52'], zone: 'B' },
  { academie: 'Rennes', departements: ['22', '29', '35', '56'], zone: 'B' },
  { academie: 'Strasbourg', departements: ['67', '68'], zone: 'B' },
  {
    academie: 'Toulouse',
    departements: ['09', '12', '31', '32', '46', '65', '81', '82'],
    zone: 'C',
  },
  { academie: 'Versailles', departements: ['78', '91', '92', '95'], zone: 'C' },
]
