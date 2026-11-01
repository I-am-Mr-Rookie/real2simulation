import GuessClient from './GuessClient.jsx';

export const metadata = { title: 'Guess the Gravity', robots: { index: false } };

export default async function Guess({ params }) {
  return <section className="page-wide">
    <p className="eyebrow">Public · no account needed</p>
    <h1>Guess the Gravity</h1>
    <GuessClient token={(await params).token} />
  </section>;
}
