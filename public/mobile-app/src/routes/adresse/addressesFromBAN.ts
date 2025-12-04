export type PropertiesFromBAN = {
  city: string
  context: string
  id: string
  label: string
  name: string
  postcode: string
}

export type FeatureFromBAN = {
  properties: PropertiesFromBAN
}

export type ResponseFromBAN = {
  type: string
  features: FeatureFromBAN[]
  query: string
}

export class AddressFromBAN {
  private _city: string = ''
  private _context: string = ''
  private _id: string = ''
  private _label: string = ''
  private _name: string = ''
  private _postcode: string = ''

  constructor(
    city: string,
    context: string,
    id: string,
    label: string,
    name: string,
    postcode: string
  ) {
    this._city = city
    this._context = context
    this._id = id
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

  get id(): string {
    return this._id
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

export const callBAN = async (inputValue: string) => {
  try {
    const encodedInputValue = encodeURI(inputValue)
    const endpoint_headers = {
      accept: 'application/json',
    }
    const response = await fetch(
      `https://data.geopf.fr/geocodage/search?q=${encodedInputValue}&autocomplete=1&index=address&limit=10&returntruegeometry=false`,
      {
        headers: endpoint_headers,
      }
    )
    const result = await response.json()
    console.log(result)

    if (
      result.code === 400 &&
      result.detail[0] ==
        'q: must contain between 3 and 200 chars and start with a number or a letter' &&
      result.message == 'Failed parsing query'
    ) {
      return { statusCode: 400 }
    }

    return {
      statusCode: 200,
      results: formatResults(result),
    }
  } catch (error) {
    console.error(error)
  }
  return {}
}

const formatResults = (data: ResponseFromBAN) => {
  const results = [] as AddressFromBAN[]
  if (data) {
    data.features.forEach((feature: FeatureFromBAN) => {
      const city = feature.properties.city
      const context = feature.properties.context
      const id = feature.properties.id
      const label = feature.properties.label
      const name = feature.properties.name
      const postcode = feature.properties.postcode
      const address = new AddressFromBAN(city, context, id, label, name, postcode)
      results.push(address)
    })
  }
  console.log(results)
  return results
}
