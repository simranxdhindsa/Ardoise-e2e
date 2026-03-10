import { faker } from '@faker-js/faker';

faker.locale = 'en';

export const TestData = {
  user: {
    email: () => faker.internet.email(),
    password: () => faker.internet.password(12, false, /[A-Za-z0-9!@#$%]/),
    firstName: () => faker.name.firstName(),
    lastName: () => faker.name.lastName(),
    fullName: () => `${faker.name.firstName()} ${faker.name.lastName()}`,
  },

  course: {
    title: () => faker.lorem.sentence(4),
    description: () => faker.lorem.paragraph(2),
    slug: () => faker.helpers.slugify(faker.lorem.words(3)).toLowerCase(),
    longTitle: () => faker.lorem.words(20).substring(0, 100),
    longDescription: () => faker.lorem.paragraphs(3).substring(0, 1000),
  },

  project: {
    name: () => `Test Project ${faker.datatype.uuid().substring(0, 8)}`,
    description: () => faker.lorem.paragraph(2),
  },

  xss: {
    scriptTag: '<script>alert("xss")</script>',
    imgOnerror: '<img src=x onerror=alert(1)>',
    eventHandler: '<b onmouseover=alert(1)>test</b>',
    javascriptUrl: 'javascript:alert(1)',
  },

  generateUser: () => ({
    email: faker.internet.email(),
    password: faker.internet.password(12),
    firstName: faker.name.firstName(),
    lastName: faker.name.lastName(),
  }),
};
