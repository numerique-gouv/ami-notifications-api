export type AddressFromBAN = {
  city: string
  context: string
  label: string
  name: string
  postcode: string
}

export const callBAN = async (inputValue) => {
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

    return formatResults(result)
  } catch (error) {
    console.error(error)
  }
}

const formatResults = (data) => {
  const results = [] as AddressFromBAN[]
  if (data) {
    data.features.forEach((feature) => {
      const address = {} as AddressFromBAN
      address.city = feature.properties.city
      address.context = feature.properties.context
      address.label = feature.properties.label
      address.name = feature.properties.name
      address.postcode = feature.properties.postcode
      results.push(address)
    })
  }
  console.log(results)
  return results
}
