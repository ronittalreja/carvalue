export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10 space-y-6">
      <h1 className="text-2xl font-bold">About / How It Works</h1>
      <p>
        This app estimates resale values for cars based on your selections: company, model, year, fuel type, kilometers driven, transmission, and ownership. 
        <br />
        Predictions are powered by a <strong>Random Forest Regressor</strong>, trained on historical car sales data, to give more accurate and nuanced estimates than linear models.
      </p>

      <h2 className="font-semibold mt-6">Demand Index</h2>
      <p>
        The Demand Index shows the relative popularity of a car model in the market. It considers the number of listings, popularity within the brand, and overall market share. 
        Higher scores indicate cars that are in greater demand.
      </p>


      <h2 className="font-semibold mt-6">Model</h2>
      <p>
        Currently using a <strong>Random Forest Regressor</strong> for price predictions. This model considers multiple features and their interactions to provide realistic estimates.
      </p>

      <h2 className="font-semibold mt-6">Contact Us</h2>
      <p>
        For feedback, questions, or dataset contributions, you can reach out at:
        <br />
        <a href="mailto:support@carpricedashboard.com" className="text-blue-600 underline">
          ronittwork@gmail.com
        </a>
      </p>

      <p className="text-sm text-gray-600 mt-6">
        Disclaimer: Prices and demand indices are estimates based on available data; actual market values may vary.
      </p>
    </div>
  )
}
