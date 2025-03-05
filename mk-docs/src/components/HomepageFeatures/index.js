import React from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css'; // Make sure this path is correct

const FeatureList = [
  {
    title: 'Ingestion',
    Svg: require('@site/static/img/LetterI.svg').default,
    description: (
      <>

      </>
    ),
  },
  {
    title: 'Data Load',
    Svg: require('@site/static/img/LetterD.svg').default,
    description: (
      <>

      </>
    ),
  },
  {
    title: 'Enrichment',
    Svg: require('@site/static/img/LetterE.svg').default,
    description: (
      <>

      </>
    ),
  },
  {
    title: 'Analysis',
    Svg: require('@site/static/img/LetterA.svg').default,
    description: (
      <>

      </>
    ),
  },
  {
    title: 'Story Telling Visualization',
    Svg: require('@site/static/img/LetterS.svg').default,
    description: (
      <>

      </>
    ),
  },
];

function FeatureCard({Svg, title, description}) {
  return (
    <div className={clsx('col col--2')}>
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          {Svg && (
            <div className={styles.cardImage}>
              <Svg className={styles.featureSvg} role="img" />
            </div>
          )}
          <div className={styles.cardTitle}>
            <Heading as="h3">{title}</Heading>
          </div>
        </div>
        <div className={styles.cardBody}>
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <FeatureCard key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}