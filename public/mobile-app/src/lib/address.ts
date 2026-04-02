type AddressJSON = {
  _city: string;
  _context: string;
  _idBAN: string;
  _label: string;
  _name: string;
  _postcode: string;
};

export class Address {
  constructor(
    private _city: string = '',
    private _context: string = '',
    private _idBAN: string = '',
    private _label: string = '',
    private _name: string = '',
    private _postcode: string = ''
  ) {}

  static fromJSON(json: Address | AddressJSON): Address {
    if (json instanceof Address) {
      return json;
    }
    return new Address(
      json._city,
      json._context,
      json._idBAN,
      json._label,
      json._name,
      json._postcode
    );
  }

  get city(): string {
    return this._city;
  }

  get context(): string {
    return this._context;
  }

  get idBAN(): string {
    return this._idBAN;
  }

  get label(): string {
    return this._label;
  }

  get name(): string {
    return this._name;
  }

  get postcode(): string {
    return this._postcode;
  }

  get departement(): string {
    if (this._postcode.length < 2) {
      return '';
    }
    const departement = this._postcode.substring(0, 2);

    if (!['97', '98'].includes(departement)) {
      return departement;
    }

    // if postcode startswith 97 and 98, departement has 3 digits
    if (this._postcode.length < 3) {
      return '';
    }
    return this._postcode.substring(0, 3);
  }

  get zone(): string {
    const zone = zones.find((z) => {
      return z.departements.includes(this.departement);
    });
    return zone ? zone.label : '';
  }
}

const zones = [
  {
    label: 'Zone A',
    departements: [
      '01',
      '03',
      '07',
      '15',
      '16',
      '17',
      '19',
      '21',
      '23',
      '24',
      '25',
      '26',
      '33',
      '38',
      '39',
      '40',
      '42',
      '43',
      '47',
      '58',
      '63',
      '64',
      '69',
      '70',
      '71',
      '73',
      '74',
      '79',
      '86',
      '87',
      '89',
      '90',
    ],
  },
  {
    label: 'Zone B',
    departements: [
      '02',
      '04',
      '05',
      '06',
      '08',
      '10',
      '13',
      '14',
      '18',
      '22',
      '27',
      '28',
      '29',
      '35',
      '36',
      '37',
      '41',
      '44',
      '45',
      '49',
      '50',
      '51',
      '52',
      '53',
      '54',
      '55',
      '56',
      '57',
      '59',
      '60',
      '61',
      '62',
      '67',
      '68',
      '72',
      '76',
      '80',
      '83',
      '84',
      '85',
      '88',
    ],
  },
  {
    label: 'Zone C',
    departements: [
      '09',
      '11',
      '12',
      '30',
      '31',
      '32',
      '34',
      '46',
      '48',
      '65',
      '66',
      '75',
      '77',
      '78',
      '81',
      '82',
      '91',
      '92',
      '93',
      '94',
      '95',
    ],
  },
  { label: 'Corse', departements: ['20'] },
  { label: 'Guadeloupe', departements: ['971', '977', '978'] },
  { label: 'Guyane', departements: ['973'] },
  { label: 'Martinique', departements: ['972'] },
  { label: 'Mayotte', departements: ['976'] },
  { label: 'Nouvelle Calédonie', departements: ['988'] },
  { label: 'Polynésie', departements: ['987'] },
  { label: 'Réunion', departements: ['974'] },
  { label: 'Saint Pierre et Miquelon', departements: ['975'] },
  { label: 'Wallis et Futuna', departements: ['986'] },
];
