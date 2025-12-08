export class Address {
  private _city: string
  private _context: string
  private _idBAN: string
  private _label: string
  private _name: string
  private _postcode: string

  constructor(
    city: string = '',
    context: string = '',
    idBAN: string = '',
    label: string = '',
    name: string = '',
    postcode: string = ''
  ) {
    this._city = city
    this._context = context
    this._idBAN = idBAN
    this._label = label
    this._name = name
    this._postcode = postcode
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
}
