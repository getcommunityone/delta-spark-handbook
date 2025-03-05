import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner, 'hero--primary')}>
      <div className="container">
        <Heading as="h1" style= {{color:'black'}}  className="hero__title">{siteConfig.title}</Heading>
        <p style={{color:'black'}} className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--lg"
            style={{ backgroundColor: '#ff6347', color: 'white', marginRight: '10px' }}
            to="/docs/intro">
            Explore demos
          </Link>
          <Link
            className="button button--lg"
            style={{ borderColor: '#ff6347', color: '#ff6347', borderWidth: '1px', borderStyle: 'solid' }}
            to="/docs/intro">
            Learn more
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Community for ${siteConfig.title}`}
      description="Cloud and Data Architecture">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
